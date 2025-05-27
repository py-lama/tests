"""Integration tests for MQTT endpoints using pytest-mqtt."""
import json
import time
import pytest
from paho.mqtt import client as mqtt

# Test message data
TEST_MESSAGE = {
    "test": "data",
    "value": 42,
    "active": True,
    "nested": {"key": "value"}
}

# Test topics
TEST_TOPIC_PUBLISH = "test/publish"
TEST_TOPIC_SUBSCRIBE = "test/subscribe"


def test_mqtt_connection(mosquitto):
    """Test that we can connect to the MQTT broker."""
    client = mqtt.Client()
    client.connect(mosquitto.host, mosquitto.port)
    assert client.is_connected() is False  # Not connected yet
    client.loop_start()
    time.sleep(0.1)  # Give it a moment to connect
    assert client.is_connected() is True
    client.disconnect()
    client.loop_stop()


def test_mqtt_publish_subscribe(mosquitto):
    """Test publishing and subscribing to MQTT topics."""
    received_messages = []
    
    def on_connect(client, userdata, flags, rc, properties=None):
        client.subscribe(TEST_TOPIC_SUBSCRIBE)
    
    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
        except json.JSONDecodeError:
            payload = msg.payload.decode()
        received_messages.append({
            "topic": msg.topic,
            "payload": payload,
            "qos": msg.qos,
            "retain": msg.retain
        })
    
    # Create and configure client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Connect and start the loop
    client.connect(mosquitto.host, mosquitto.port)
    client.loop_start()
    
    # Wait for connection and subscription
    time.sleep(0.2)
    
    # Publish a test message
    test_msg = {"test": "message", "value": 42}
    result = client.publish(TEST_TOPIC_SUBSCRIBE, json.dumps(test_msg))
    result.wait_for_publish()
    
    # Wait for the message to be received
    timeout = time.time() + 2  # 2 second timeout
    while not received_messages and time.time() < timeout:
        time.sleep(0.1)
    
    # Verify the message was received
    assert len(received_messages) == 1
    assert received_messages[0]["topic"] == TEST_TOPIC_SUBSCRIBE
    assert received_messages[0]["payload"] == test_msg
    
    # Clean up
    client.loop_stop()
    client.disconnect()


@pytest.mark.parametrize("qos", [0, 1, 2])
def test_mqtt_qos_levels(mosquitto, qos):
    """Test different QoS levels for MQTT messages."""
    received_messages = []
    topic = f"{TEST_TOPIC_SUBSCRIBE}/qos{qos}"
    
    def on_connect(client, userdata, flags, rc, properties=None):
        client.subscribe(topic, qos=qos)
    
    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
        except json.JSONDecodeError:
            payload = msg.payload.decode()
        received_messages.append({
            "topic": msg.topic,
            "payload": payload,
            "qos": msg.qos,
            "retain": msg.retain
        })
    
    # Create and configure client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Connect and start the loop
    client.connect(mosquitto.host, mosquitto.port)
    client.loop_start()
    
    # Wait for connection and subscription
    time.sleep(0.2)
    
    # Publish a test message with the specified QoS
    test_msg = {"qos_test": qos, "message": f"Testing QoS {qos}"}
    result = client.publish(topic, json.dumps(test_msg), qos=qos)
    result.wait_for_publish()
    
    # Wait for the message to be received
    timeout = time.time() + 2  # 2 second timeout
    while not received_messages and time.time() < timeout:
        time.sleep(0.1)
    
    # Verify the message was received with the correct QoS
    assert len(received_messages) == 1
    assert received_messages[0]["topic"] == topic
    assert received_messages[0]["payload"] == test_msg
    assert received_messages[0]["qos"] == qos
    
    # Clean up
    client.loop_stop()
    client.disconnect()


def test_mqtt_retained_messages(mosquitto):
    """Test MQTT retained messages."""
    topic = f"{TEST_TOPIC_SUBSCRIBE}/retained"
    received_messages = []
    
    def on_connect(client, userdata, flags, rc, properties=None):
        client.subscribe(topic)
    
    def on_message(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode()) if msg.payload else {}
        except json.JSONDecodeError:
            payload = msg.payload.decode() if msg.payload else {}
        received_messages.append({
            "topic": msg.topic,
            "payload": payload,
            "qos": msg.qos,
            "retain": msg.retain
        })
    
    # First client to publish a retained message
    pub_client = mqtt.Client()
    pub_client.connect(mosquitto.host, mosquitto.port)
    pub_client.loop_start()
    
    # Publish a retained message
    retained_msg = {"type": "retained", "value": "This is a retained message"}
    pub_client.publish(topic, json.dumps(retained_msg), retain=True)
    time.sleep(0.2)  # Give it time to be retained
    
    # Second client to subscribe and receive the retained message
    sub_client = mqtt.Client()
    sub_client.on_connect = on_connect
    sub_client.on_message = on_message
    sub_client.connect(mosquitto.host, mosquitto.port)
    sub_client.loop_start()
    
    # Wait for the retained message
    timeout = time.time() + 2
    while not received_messages and time.time() < timeout:
        time.sleep(0.1)
    
    # Verify the retained message was received
    assert len(received_messages) == 1
    assert received_messages[0]["topic"] == topic
    assert received_messages[0]["payload"] == retained_msg
    assert received_messages[0]["retain"] is True
    
    # Clean up
    pub_client.loop_stop()
    pub_client.disconnect()
    sub_client.loop_stop()
    sub_client.disconnect()
    
    # Clear the retained message
    clear_client = mqtt.Client()
    clear_client.connect(mosquitto.host, mosquitto.port)
    clear_client.loop_start()
    clear_client.publish(topic, retain=True)  # Empty retained message
    time.sleep(0.2)
    clear_client.loop_stop()
    clear_client.disconnect()
