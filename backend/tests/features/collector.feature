Feature: Property Collector
  As an investor
  I want the system to collect properties from multiple sources
  So that I can identify new investment opportunities

  Background:
    Given collection criteria with min price 100000 and max price 500000

  Scenario: Collect properties from a source adapter
    Given a source adapter that returns 3 properties
    When I run the collector
    Then the result shows 3 properties found
    And the result shows 3 new properties
    And the result shows 0 skipped properties

  Scenario: Deduplicate already-seen properties
    Given a source adapter that returns 2 properties
    And 1 of those properties was already seen
    When I run the collector
    Then the result shows 2 properties found
    And the result shows 1 new properties
    And the result shows 1 skipped properties

  Scenario: Handle source adapter failure gracefully
    Given a source adapter that raises an error
    When I run the collector
    Then the result shows 0 properties found
    And the result contains an error message

  Scenario: Run collection across multiple sources
    Given a Zillow adapter returning 2 properties
    And a Realtor adapter returning 1 property
    When I run the collector
    Then the collection result has 2 source results
    And the total new properties across all sources is 3

  Scenario: Update collection criteria via API
    Given the API is running
    When I PUT criteria with min price 200000 and max price 800000
    Then GET criteria returns min price 200000

  Scenario: Trigger manual collection run via API
    Given the API is running
    And collection criteria is configured
    When I POST to /api/v1/collector/run
    Then the response contains a list of collection results
