package edu.brown.cs;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import edu.brown.cs.searcher.StopWords;
import edu.brown.cs.searcher.Tsearch;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.TestInstance.Lifecycle;

import org.typesense.api.FieldTypes;

/**
 * Unit test for simple App.
 */
public class TsearchTest {

    static boolean isServerRunning = false;
    static StopWords sWords = new StopWords(List.of("a", "the"));
    Tsearch searcher;

    @BeforeAll
    public void setup() throws Exception {
        this.searcher = new Tsearch(sWords);
        this.searcher.addField("id", FieldTypes.INT32, false);
        this.searcher.addField("description", FieldTypes.STRING, false);
        this.searcher.addField("year", FieldTypes.INT32, true);

        Map<String, Object> firstDoc = new HashMap<String, Object>();
        firstDoc.put("id", 1);
        firstDoc.put("year", "1999");
        firstDoc.put("id", "Everything changed when the Fire Nation attacked");
        this.searcher.makeCollection("stuff", "id");
        this.searcher.createDocument(firstDoc);
    }

    @Test
    public void simpleTest() {
        if (isServerRunning) {
            assertTrue(true);
        }
    }

}
