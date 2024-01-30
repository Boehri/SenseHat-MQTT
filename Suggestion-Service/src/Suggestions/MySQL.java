package Suggestions;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class MySQL {
	
	private static final String host = "localhost";
	private static final String port = "3306";
	private static final String database = "mysql-mqtt";
	private static final String username = "root";
	private static final String password = "";
	private static Connection con;
	
	public static boolean isConnected() {
		return (con == null ? false : true);
	}
	
	public static Connection connect() throws ClassNotFoundException {
		if (!isConnected()) {
			try { //connect to database
			Class.forName("com.mysql.cj.jdbc.Driver");
				con = DriverManager.getConnection("jdbc:mysql://"+host+":"+port+"/" + database,username,password);
				
				
			} catch (SQLException e) {
				System.out.println("Connection unsuccessful");
				e.printStackTrace();
			}
		}
		return con;
	}
	public static void disconnect() {
		if(isConnected()) {
			try {
				con.close();
				System.out.println("Disconnected");
			} catch (SQLException e) {
				e.printStackTrace();
			}
		}
	}
	public static void update(String q) {
		PreparedStatement ps; //Update on database
		try {
			ps = con.prepareStatement(q);
			ps.execute();
		} catch (SQLException e) {
			e.printStackTrace();
		}
	}
}
