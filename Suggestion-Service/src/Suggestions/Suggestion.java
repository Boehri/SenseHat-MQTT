package Suggestions;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Date;

import org.json.JSONException;
import org.json.JSONObject;

public class Suggestion {
	static Connection conn;
	public static void createSuggestion(double d) {
		int id;
		if(d<=5) { //Winter
			id = 1;
		}
		else if(d<=20) {//Frühling und Herbst
			if(getCurrentMonth() < 6) {
				id = 2;
			}
			else {
				id = 4;
			}
		}
		else { //Sommer
			id = 3;
		}
		selectSuggestion(id);
	}
	private static void selectSuggestion(int id) {
		try {
			//Connect to MySQL
				conn = MySQL.connect();
				String query = "SELECT * FROM kleidung WHERE ID = "+id;
			    // create the java statement
			    Statement st = conn.createStatement();
			    // execute the query, and get a java resultset
			    ResultSet rs = st.executeQuery(query);
			    while (rs.next())
			    {	//Handle Data
			      String name = rs.getString("Name");
			      String output = "Kleidungsempfehlung: " +name;
			      System.out.println(output);
			      BrokerConnection.publishMessage(createJSON(name), "raspi/out/sug");
			      break;
			      
			}
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	   }
	private static int getCurrentMonth() {
		//Get month of current date as int
		Date date = new Date();
		LocalDate localDate = date.toInstant().atZone(ZoneId.systemDefault()).toLocalDate();
		int month = localDate.getMonthValue();
		return month;
	}
	public static JSONObject createJSON(String value) {
		//create json message to publish
		JSONObject jsonMessage = new JSONObject();
		try {
			jsonMessage.put("suggestion", value);
		} catch (JSONException e) {
			e.printStackTrace();
		}
		return jsonMessage;
	}

}
