package edu.brown.cs.searcher;

import java.util.LinkedList;
import java.util.List;
import org.typesense.model.SearchParameters;

public final class SearchParamBuilder {
  private final SearchParameters params = new SearchParameters();
  private List<String> filterStrings;

  public SearchParamBuilder(String keyphrase) {
    this.filterStrings = new LinkedList<>();
    params
        .q(keyphrase)
        .queryBy("latestAgenda, latestMinutes, body")
        .facetBy("body")
        .perPage(250)
        .maxFacetValues(250);
  }

  public SearchParamBuilder withBody(String publicBody) {
    filterStrings.add(String.format("body:=%s", publicBody));
    return this;
  }

  public SearchParamBuilder withDateStart(int dateStart) {
    filterStrings.add(String.format("meeting_dt: >=%s",  dateStart));
    return this;
  }

  public SearchParamBuilder withDateEnd(int dateEnd) {
    filterStrings.add(String.format("meeting_dt: <=%s",dateEnd));
    return this;
  }

  public SearchParameters build() {
    if (filterStrings.isEmpty()) {
      return params;
    } else {
      String filterQuery = String.join(" && ", filterStrings);
      return params.filterBy(filterQuery);
    }
  }
}
