package edu.brown.cs.server;


import static spark.Spark.after;

import java.util.List;

import org.typesense.api.FieldTypes;

import com.google.protobuf.Int32Value;

import edu.brown.cs.searcher.StopWords;
import edu.brown.cs.searcher.Tsearch;
import spark.Spark;
/*
 * top level class where we use spark to start the server and run endpoint handlers
 */
public class Server {

        // TODO: add more :)
        static StopWords sWords = new StopWords(List.of("a", "the", "you", "we", "me", "i", "them", "this", "that", "is", "and", "but", "as", "or"));
        public static void main(String[] args) {
        Spark.port(3232);

        after((request, response) -> {
            response.header("Access-Control-Allow-Origin", "*");
            response.header("Access-Control-Allow-Methods", "*");
        });

        // setup typesense
        Tsearch searcher = new Tsearch(sWords);
        try {
            // add appropriate fields
            searcher.addField("id", FieldTypes.STRING, false);
            searcher.addField("body", FieldTypes.STRING, true);
            searcher.addField("meeting_dt", FieldTypes.FLOAT, true);
            searcher.addField("address", FieldTypes.STRING, false);
            searcher.addField("filing_dt", FieldTypes.FLOAT, true);
            searcher.addField("is_emergency", FieldTypes.BOOL, true);
            searcher.addField("is_annual_calendar", FieldTypes.BOOL, false);
            searcher.addField("is_public_notice", FieldTypes.BOOL, false);
            searcher.addField("is_cancelled", FieldTypes.BOOL, false);
            searcher.addField("cancelled_dt", FieldTypes.FLOAT, false);
            searcher.addField("cancelled_reason", FieldTypes.STRING, false);
            searcher.addField("latestAgenda", FieldTypes.STRING, false);
            searcher.addField("latestAgendaLink", FieldTypes.STRING, false);
            searcher.addField("latestMinutes", FieldTypes.STRING, false);
            searcher.addField("latestMinutesLink", FieldTypes.STRING, false);
            searcher.addField("contactPerson", FieldTypes.STRING, true);
            searcher.addField("contactEmail", FieldTypes.STRING, false);
            searcher.addField("contactPhone", FieldTypes.STRING, false);

            // create collection 
            searcher.makeCollection("meetings", "id");
            // TODO: make documents
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        // put in all the endpoint handlers
        Spark.get("meetingSearch", new LoadMeetingHandler(searcher));
        Spark.get("getMeeting", new SearchHandler(searcher));
        Spark.init();
        Spark.awaitInitialization();
        System.out.println("Server started.");
    }
}
