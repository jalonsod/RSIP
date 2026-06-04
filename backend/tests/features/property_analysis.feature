Feature: Property Investment Analysis
  As a real estate investor
  I want to analyze a property's investment potential
  So that I can make informed purchase decisions

  Background:
    Given a property with zpid "12345678"

  Scenario: Analyze property with all data sources returning data
    Given a Zillow property adapter returning price 350000 sqft 1500 beds 3 baths 2
    And a Zillow rental estimate adapter returning expected rent 2200
    And a comparables adapter returning 5 neighbors with avg price 340000
    When I analyze the property
    Then the analysis zpid is "12345678"
    And the analysis price is 350000
    And the analysis expected rent is 2200.0
    And the analysis price per sqft is 233.33
    And the analysis price vs neighbors delta is 10000
    And the analysis data sources include "zillow_property"
    And the analysis data sources include "zillow_rent_estimate"
    And the analysis data sources include "comparables"
    And the analysis has no errors

  Scenario: Analyze property with missing rent estimate
    Given a Zillow property adapter returning price 300000 sqft 1200 beds 2 baths 1
    And a failing Zillow rental estimate adapter
    And a comparables adapter returning 3 neighbors with avg price 295000
    When I analyze the property
    Then the analysis zpid is "12345678"
    And the analysis price is 300000
    And the analysis expected rent is None
    And the analysis data sources include "zillow_property"
    And the analysis data sources include "comparables"
    And the analysis contains an error from "zillow_rent_estimate"

  Scenario: Analyze property with all adapters failing
    Given a failing Zillow property adapter
    And a failing Zillow rental estimate adapter
    And a failing comparables adapter
    When I analyze the property
    Then the analysis zpid is "12345678"
    And the analysis has 3 errors

  Scenario: Retrieve cached analysis via API
    Given the API is running
    And property analysis for zpid "12345678" is cached
    When I GET analysis for zpid "12345678"
    Then the response status is 200
    And the response zpid is "12345678"

  Scenario: Request analysis for unknown zpid via API
    Given the API is running
    When I GET analysis for zpid "99999999"
    Then the response status is 404

  Scenario: Analyze property via POST API endpoint
    Given the API is running
    When I POST analyze for zpid "12345678"
    Then the response status is 200
    And the response zpid is "12345678"
