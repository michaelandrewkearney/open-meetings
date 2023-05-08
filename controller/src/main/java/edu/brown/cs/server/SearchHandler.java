package edu.brown.cs.server;

import com.squareup.moshi.JsonAdapter;
import com.squareup.moshi.Moshi;

import edu.brown.cs.searcher.SearchParamBuilder;
import edu.brown.cs.searcher.Tsearch;
import edu.brown.cs.server.helpers.MeetingData;
import java.util.List;
import java.util.Map;
import org.typesense.model.FacetCounts;
import org.typesense.model.SearchParameters;
import org.typesense.model.SearchResult;
import org.typesense.model.SearchResultHit;
import spark.Request;
import spark.Response;
import spark.Route;


/**
 * This is the SearchHandler. It handles the query "meetingSearch", which
 * loads a Meeting.
 */
public class SearchHandler implements Route {
    private final Tsearch searcher;
    public SearchHandler(Tsearch searcher) {
        this.searcher = searcher;
    }


    /**
     * This is what is called when a request is made.
     * @param request - request
     * @param response - response
     * @return - appropriate response object
     * @throws Exception
     */
    @Override
    public Object handle(Request request, Response response) throws Exception {
        String keyphrase = request.queryParams("keyphrase");

        //if no param query
        if (keyphrase == null) {
            return new SearchRequestFailureResponse("Must include an 'id' query.").serialize();
        }

        String publicBody = request.queryParams("publicBody");
        String dateStart = request.queryParams("dateStart"); // epoch time (seconds)
        String dateEnd = request.queryParams("dateEnd"); // epoch time (seconds)

        SearchParamBuilder paramBuilder = new SearchParamBuilder(keyphrase);
        if (publicBody != null) {
            paramBuilder.withBody(publicBody);
        }
        if (dateStart != null) {
            paramBuilder.withDateStart(Integer.parseInt(dateStart));
        }
        if (dateEnd != null) {
            paramBuilder.withDateEnd(Integer.parseInt(dateEnd));
        }

        // need to take in meeting results from searcher? and return the necessary info
        try {
            // this is where we get data from Tsearcher
            SearchResult searchResult = searcher.searchMeetings(paramBuilder.build());
            SearchSuccessResponse successResp = new SearchSuccessResponse(
                searchResult.getFound(),
                searchResult.getOutOf(),
                searchResult.getFacetCounts(),
                searchResult.getHits()
            );
            return successResp.serialize();
        } catch (Exception e) {
            e.printStackTrace();
            return new SearchDatasourceFailureResponse("Invalid Meeting.").serialize();
        }

    }

    /**
     * Success response object.
     * @param response_type - success
     */
    public record SearchSuccessResponse(String response_type, int found, int out_of, List<FacetCounts> facet_counts, List<SearchResultHit> hits) {
        public SearchSuccessResponse(int found, int out_of, List<FacetCounts> facet_counts, List<SearchResultHit> hits) {
            this("success", found, out_of, facet_counts, hits);
        }
        String serialize() {
            try {
                Moshi moshi = new Moshi.Builder()
                        .build();
                JsonAdapter<SearchSuccessResponse> adapter = moshi.adapter(SearchSuccessResponse.class);
                return adapter.toJson(this);
            } catch(Exception e) {
                e.printStackTrace();
                throw e;
            }
        }
    }

    /**
     * Response object to send if someone requested an invalid meeting
     */
    public record SearchJsonFailureResponse(String response_type, String output) {
        public SearchJsonFailureResponse(String output) { this("error_bad_json", output); }

        /**
         * @return this response, serialized as Json
         */
        String serialize() {
            Moshi moshi = new Moshi.Builder().build();
            return moshi.adapter(SearchJsonFailureResponse.class).toJson(this);
        }
    }

    /**
     * Response object to send if someone requested soup before any recipes were loaded
     */
    public record SearchRequestFailureResponse(String response_type, String output) {
        public SearchRequestFailureResponse(String output) { this("error_bad_request", output); }

        /**
         * @return this response, serialized as Json
         */
        String serialize() {
            Moshi moshi = new Moshi.Builder().build();
            return moshi.adapter(SearchRequestFailureResponse.class).toJson(this);
        }
    }

    /**
     * Response object to send if someone requested soup before any recipes were loaded
     */
    public record SearchDatasourceFailureResponse(String response_type, String output) {
        public SearchDatasourceFailureResponse(String output) { this("error_datasource", output); }

        /**
         * @return this response, serialized as Json
         */
        String serialize() {
            Moshi moshi = new Moshi.Builder().build();
            return moshi.adapter(SearchDatasourceFailureResponse.class).toJson(this);
        }
    }

}
