package edu.brown.cs.searcher;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import java.util.Optional;
import org.typesense.api.*;
import org.typesense.model.*;
import org.typesense.resources.*;

/**
 * class that represents a Typesense searcher; connects to the server and makes 
 * requests to it 
 * 
 * TODO: represents a singular collection as of now
 */
public class Tsearch {
    private List<Node> nodes;
    private Configuration config;
    private Client client;
    private List<Field> fields;
    private String collectionName;
    private List<String> stop_words;

    public Tsearch(StopWords stopWords) {
        // connect to the node we are running locally
        List<Node> nodes = new ArrayList<Node>();
        nodes.add(new Node("http", "localhost", "8108"));
        this.nodes = nodes;
        this.config = new Configuration(nodes, Duration.ofSeconds(10), System.getenv("TYPESENSE_API_KEY"));
        this.client = new Client(config);
        this.stop_words = stopWords.stop_words();
    }

    /**
     * adds a field to the typesense docs
     * @param name, name of the field
     * @param type, type of the field - MUST be taken from FieldTypes.<type>
     * @param isFacet, if the field is a facet (something that typesense adds counts to)
     */
    public void addField(String name, String type, boolean isFacet) {
        this.fields.add(new Field().name(name).type(type).facet(isFacet));
    }

    /**
     * creates a collection based off the fields input earlier
     * @param collectionName, name of the collection used to grab it later
     * @param defaultSortingField, default field to sort the collections by
     * @throws Exception, propagates exception from typesense library
     */
    public void makeCollection(String collectionName, String defaultSortingField) throws Exception {
        CollectionSchema cschema = new CollectionSchema().name(collectionName).fields(this.fields).defaultSortingField(defaultSortingField);
        this.client.collections().create(cschema);
    }

    /**
     * creates a document to the current collection
     * @param doc, map similar to json format - should be fieldName -> fieldValue
     * @throws Exception, propagates exception from typesense library
     */
    public void createDocument(Map<String,Object> doc) throws Exception {
        this.client.collections(this.collectionName).documents().create(doc);
    }
    
    /**
     * given a String representing a json of many documents, adds them to the searcher
     * @param documentList, json String of docs
     * @throws Exception, propagates exception from typesense library
     */
    public void importDocs(String documentList) throws Exception {
        ImportDocumentsParameters qParams = new ImportDocumentsParameters();
        qParams.action("create");
        this.client.collections(this.collectionName).documents().import_(documentList, qParams);
    }

    /**
     * search for the given query over the given fields to query in
     * @param query, the keyphrase to search for
     * @param queryField, the fields to search the query for
     * @return a SearchResult obj defined by the typesense library
     * @throws Exception, propagates exception from typesense library
     */
    public SearchResult searchDoc(String query, String queryField) throws Exception {
        SearchParameters params = new SearchParameters().q(query).queryBy(queryField);
        SearchResult result = client.collections(this.collectionName).documents().search(params);
        return result;
    }


    public SearchResult searchMeetings(SearchParameters params) throws Exception {
        return client.collections("meetings").documents().search(params);
    }

    public Map<String, Object> getMeeting(String id) throws Exception {
        return client.collections("meetings").documents(id).retrieve();
    }

    public Map<String, Object> getMeetingsCollection(String id) throws Exception {
        return client.collections("meetings").documents(id).retrieve();
    }


    /**
     * filters unnecessary terms out of a query, if the query is not empty afterwards
     * @param query, the query to enter
     * @return, a filtered query OR the original query if filtered is empty
     */
    private String filterQuery(String query) {
        String[] words = query.split(" "); // check all individual words
        // TODO: a regex could be better here
        String ret = "";
        
        for (String s : words) {
            if (!stop_words.contains(s)) {
                ret += s;
            }
        }
        
        if (ret.equals(""))
            return query;
        return ret;
    }



}
