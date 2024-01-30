package Suggestions;

import java.security.NoSuchAlgorithmException;
import javax.net.ssl.SSLSocketFactory;

import org.eclipse.paho.client.mqttv3.*;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.json.JSONException;
import org.json.JSONObject;


public class BrokerConnection {
	String clientID = "JavaBE";
	static MqttClient client;
	int qods = 2;
	public static void setClient() throws MqttException {
		 client = new MqttClient(
		        "ssl://5d4607be694c4b98bdfdab8fd5f11847.s2.eu.hivemq.cloud:8883", //URI
		        MqttClient.generateClientId(), //ClientId
		        new MemoryPersistence()); //Persistence
		
	}
	public void setConnection() throws NoSuchAlgorithmException {
	try { //set connection data
		setClient();
		MqttConnectOptions mco = new MqttConnectOptions();
		mco.setUserName("raspi_all");
		mco.setPassword("Raspi_all1".toCharArray());
		mco.setSocketFactory(SSLSocketFactory.getDefault());
		client.setCallback(new MqttCallback() {
		    @Override
		    // Called when the client lost the connection to the broker
		    public void connectionLost(Throwable cause) { 
		        System.out.println("client lost connection " + cause);
		    }
		    @Override
		    public void messageArrived(String topic, MqttMessage message) {
		    	try { //Handle json message
					JSONObject jobj = new JSONObject(new String(message.getPayload()));
					System.out.println(topic + ": " + jobj.getDouble("temperature"));
					Suggestion.createSuggestion(jobj.getDouble("temperature"));
				} catch (JSONException e) {
					e.printStackTrace();
				}
		    }
		    @Override
		    // Called when an outgoing publish is complete
		    public void deliveryComplete(IMqttDeliveryToken token) { 
		        System.out.println("delivery complete " + token);
		    }
		});
	 if(!client.isConnected()) { //check if client is already connected
		 client.connect(mco);
		 client.subscribe("raspi/out/temp",2); //Subscribe data
	 }
	}
	catch(Exception e) {
		e.printStackTrace();
	}
	}
	public static void publishMessage(JSONObject json, String topic) {
			//create own thread for publishing
			Thread pubthread = new Thread() {
				public void run() {
			try {
			 MqttMessage msg = new MqttMessage(json.toString().getBytes());
			 msg.setQos(0);
			 client.publish(topic,msg);
			 }
			catch(Exception e) {
				e.printStackTrace();
			}
				}}; 
		pubthread.start();
		try { //Publish ever 60 seconds
			Thread.sleep(60000);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}
	
}


/* SSLContext context = SSLContext.getInstance("SSL");
TrustManagerFactory tmf = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
KeyStore keyStore;
keyStore=KeyStore.getInstance("JKS");
keyStore.load(new FileInputStream("./mykeystore.jks"),"password".toCharArray());
tmf.init(keyStore);
context.init(null, tmf.getTrustManagers(), new SecureRandom());
MqttConnectOptions options = new MqttConnectOptions();
options.setSocketFactory(context.getSocketFactory());
options.setUserName(clientID);
options.setPassword("0000".toCharArray());
options.setCleanSession(true);

client.connect(options);
System.out.println("Connected to Broker");
MqttMessage mess = new MqttMessage(message.getBytes());
mess.setQos(qos);
client.publish(topic, mess);
client.disconnect();
System.exit(0);*/

