package Suggestions;

import java.security.NoSuchAlgorithmException;
import java.sql.Connection;
import java.sql.SQLException;

public class Main {
	static String out;
	static Connection conn;

	public static void main(String[] args) throws ClassNotFoundException, SQLException { //Connect to broker
		BrokerConnection bc = new BrokerConnection();
		try {
			bc.setConnection();
		} catch (NoSuchAlgorithmException e) {
			e.printStackTrace();
		}
    }

}
