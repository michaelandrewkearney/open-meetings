package edu.brown.cs.server;


import static spark.Spark.after;
import spark.Spark;
/*
 * top level class where we use spark to start the server and run endpoint handlers
 */
public class Server {
        public static void main(String[] args) {
        Spark.port(3232);

        after((request, response) -> {
            response.header("Access-Control-Allow-Origin", "*");
            response.header("Access-Control-Allow-Methods", "*");
        });

        // TODO: setup firestore database
        // TODO: setup typesense
        // TODO: firestore -> typesense
        
        // put in all the endpoint handlers
        Spark.get("meetingSearch", null);
        Spark.get("getMeeting", null);
        Spark.init();
        Spark.awaitInitialization();
        System.out.println("Server started.");
    }
}
