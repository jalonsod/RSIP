Feature: Zone Locator
  As an investor
  I want to analyze demographic and market data for a zip code
  So that I can make informed regional investment decisions

  Background:
    Given a zone locator query for zip code "78701" with radius 10 miles

  Scenario: Analyze zone with all adapters returning data
    Given a Census adapter returning population 50000 and growth 2.5%
    And a BLS adapter returning 25000 jobs and 3.2% unemployment
    And a Zillow zone adapter returning 120 rentals avg price 1800 days 15 and 80 sales avg price 320000 days 30
    When I analyze the zone
    Then the metrics zip code is "78701"
    And the metrics population is 50000
    And the metrics population growth is 2.5
    And the metrics jobs by radius is 25000
    And the metrics avg rental price is 1800.0
    And the metrics avg sale price is 320000.0
    And the metrics data sources include "census"
    And the metrics data sources include "bls"
    And the metrics data sources include "zillow"
    And the metrics have no errors

  Scenario: Analyze zone with partial adapter data
    Given a Census adapter returning population 30000 and growth 1.0%
    And a failing BLS adapter
    And a Zillow zone adapter returning 60 rentals avg price 1500 days 20 and 40 sales avg price 280000 days 45
    When I analyze the zone
    Then the metrics zip code is "78701"
    And the metrics population is 30000
    And the metrics data sources include "census"
    And the metrics data sources include "zillow"
    And the metrics contain an error from "bls"

  Scenario: Analyze zone with all adapters failing
    Given a failing Census adapter
    And a failing BLS adapter
    And a failing Zillow zone adapter
    When I analyze the zone
    Then the metrics zip code is "78701"
    And the metrics have 3 errors

  Scenario: Analyze zone with no adapters
    Given no adapters configured
    When I analyze the zone
    Then the metrics zip code is "78701"
    And the metrics have no errors
    And the metrics data sources list is empty

  Scenario: Retrieve cached metrics via API
    Given the API is running
    And zone metrics for zip "90210" are cached
    When I GET metrics for zip code "90210"
    Then the response status is 200
    And the response zip code is "90210"

  Scenario: Request metrics for unknown zip via API
    Given the API is running
    When I GET metrics for zip code "99999"
    Then the response status is 404

  Scenario: Analyze zone via POST API endpoint
    Given the API is running
    When I POST analyze for zip code "78701"
    Then the response status is 200
    And the response zip code is "78701"
