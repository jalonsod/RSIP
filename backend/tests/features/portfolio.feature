Feature: Portfolio Management
  As a real estate investor
  I want to manage my property portfolio
  So that I can track performance and make informed investment decisions

  Scenario: Add property to portfolio
    When I add a property with address "123 Main St" in "Austin" "TX" "78701" purchased for 350000 on "2025-01-15" currently valued at 375000 with mortgage 280000
    Then the portfolio has 1 property
    And the property address is "123 Main St"
    And the property current value is 375000

  Scenario: Record rental income
    Given a portfolio property purchased for 300000 currently valued at 320000
    When I add an active rental with monthly rent 2500
    Then the property has 1 active rental
    And the total monthly income for the property is 2500.0

  Scenario: Calculate NOI
    Given a portfolio property purchased for 400000 currently valued at 420000 with mortgage 280000
    And an active rental with monthly rent 3000
    And a maintenance expense of 1200 for the year
    When I analyze the property financials
    Then the monthly income is 3000.0
    And the annual NOI is greater than 0
    And the cap rate is greater than 0
    And the cash on cash return is greater than 0

  Scenario: Portfolio summary
    Given a portfolio property purchased for 300000 currently valued at 320000 with mortgage 200000
    And an active rental with monthly rent 2000
    And a second portfolio property purchased for 500000 currently valued at 550000 with mortgage 350000
    And an active rental on the second property with monthly rent 3500
    When I request the portfolio summary
    Then the summary shows 2 total properties
    And the total portfolio value is 870000.0
    And the total NOI is greater than 0

  Scenario: Get portfolio summary via API
    Given the API is running
    When I GET the portfolio summary
    Then the response status is 200
    And the response contains total_properties

  Scenario: Create property via API
    Given the API is running
    When I POST a new property to the portfolio API
    Then the response status is 201
    And the response contains a property id

  Scenario: Get property analysis via API
    Given the API is running
    And a property exists in the API
    When I GET the property analysis
    Then the response status is 200
    And the response contains monthly_income

  Scenario: Request analysis for unknown property via API
    Given the API is running
    When I GET analysis for a nonexistent property id
    Then the response status is 404
