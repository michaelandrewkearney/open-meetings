package edu.brown.cs.searcher;

import org.typesense.model.SearchParameters;

public final class SearchParamBuilder {
  private final SearchParameters params = new SearchParameters();

  public SearchParamBuilder(String keyphrase) {
    params
        .q(keyphrase)
        .queryBy("latestAgenda")
        .queryBy("latestMinutes")
        .queryBy("body")
        .facetBy("body");
  }

  public SearchParamBuilder withBody(String publicBody) {
    params.filterBy(String.format("body:= %s", publicBody));
    return this;
  }

  public SearchParamBuilder withDateStart(int dateStart) {
    params.filterBy(String.format("meeting_dt: >=%s", dateStart));
    return this;
  }

  public SearchParamBuilder withDateEnd(int dateEnd) {
    params.filterBy(String.format("meeting_dt: <=%s", dateEnd));
    return this;
  }

  public SearchParameters build() {
    return params;
  }
}
