```markdown
## Feature Implementation Analysis: Holiday Management

### 1. Feature Overview:

This feature allows airline users to define and manage holiday lists (including non-business days) within the GroupRM application. The primary goal is to alert approvers when fare or name list validities expire on holidays, enabling them to adjust time limits accordingly.  The system also supports automatic adjustment of validity dates in autopilot mode, shifting expiry dates to the next or previous working day.

### 2. Technical Changes:

The provided patch introduces several modifications related to holiday management and validity checks. Key changes include:

*   **Ad-hoc Group Request**: Added a flag to capture if itinerary was changed for clone requests.
*   **Holiday Calendar**: Added functionality to hide the advanced search functionality when the holiday list is created.
*   **History**: Modified access modifier of `_setRequestMasterHistoryId` to `public`
*   **Timeline Extension**: Modified the payment validity display logic to handle timezone configurations and payment validity types.
*   **Holiday List Interface**: Significant changes to validity checks, including fetching, processing, and adjusting validity dates based on holiday settings. This includes logic for handling payment validity, name list validity, and integration with the contract manager for validity adjustments. Enhanced payment validity logic to handle most restrictive scenarios and to avoid holiday check if the payment status is paid.
*   **Menu**: Added null check for `$this->_OobjResponse` to prevent errors if the object is not initialized.
*   **Ad-hoc Quote Request**: Added logic to determine if the request should be treated as modified based on the 'instantDateChange' flag or cloning.
*   **Passenger Details**: Modified the dependency field validation alert message.
*   **Database**: Added configuration to control via flights.
*   **SSO**: Unset deeplink session while login with grmAccess
*   **Deeplink**: Added logic to display deeplink header in the login page
*   **Fare Check**: Fixed an issue where the "Show More" button was not working correctly after modifying a request.
*   **Process Request**: Added logic to remove through flights from the flight number when checking seat availability.

### 3. Implementation Mapping:

The code changes implement the BRD requirements as follows:

*   **Holiday List Creation**: The changes in `holiday_calendar.js` and `class.tpl.holidayListInterface.php` directly support the creation and management of holiday lists, as described in the "Creating Holiday list" section of the BRD.
*   **Validity Checks**: The core logic for checking validities against holiday dates is implemented in `class.tpl.holidayListInterface.php`, specifically within the `_getHolidaySkipData` and `_validityCheckContract` methods.  These methods implement the process described in the "Holiday Management Process Flow" section, including alerting users and adjusting validity dates. This part of the implementation is the most complex.
*   **Autopilot Policy**: The `_validityCheckContract` method in `class.tpl.holidayListInterface.php` also handles the automatic adjustment of validity dates for autopilot policies, as described in the BRD.
*   **Alert Pop-up**: The logic to determine when to display the alert pop-up, as shown in the "Example Scenario" of the BRD, is embedded within the validity check logic in `class.tpl.holidayListInterface.php`.
*   **Cloning**: The itinerary change flag added to adhocGroupRequest.js and the logic in class.module.adhocGetQuoteRequest.php handle the scenario where a cloned request needs to be considered a modified request.

### 4. Files Modified:

*   `lib/script/moduleJs/adhocGroupRequest.js`: Added logic to capture if itinerary was changed for clone requests.
*   `lib/script/moduleJs/holiday_calendar.js`: Implemented the logic to hide the advanced search functionality when the holiday list is created.
*   `classesTpl/class.tpl.viewHistory.php`: Modified access modifier of `_setRequestMasterHistoryId` to `public`
*   `classesTpl/class.tpl.timeLineExtensionV1.php`: Modified the payment validity display logic to handle timezone configurations and payment validity types.
*   `classesTpl/class.tpl.holidayListInterface.php`: Implemented the main holiday management logic, including validity checks and adjustments.
*   `classesModule/class.module.menuV1.php`: Added null check for `$this->_OobjResponse` to prevent errors if the object is not initialized.
*   `classesModule/class.module.adhocGetQuoteRequest.php`: Added logic to determine if the request should be treated as modified based on the 'instantDateChange' flag or cloning.
*   `classesModule/class.module.submitTigerPaymentRequest.php`: Added script to hide content loader
*   `language/en_language/en_validation.conf`: Modified the dependency field validation alert message.
*   `database/WN_database.sql`: Added configuration to control via flights.
*   `SSO/oauthSSO.php`: Unset deeplink session while login with grmAccess
*   `smarty/templates/createPassengerTemplateExtJs.tpl`: Modified the dependency field validation alert message.
*   `smarty/templates/groupLevelTimelineExtensionExtJs.tpl`: Added condition to prevent from overriding payment validity type when fareTypeDetails is present
*   `plugins/WN/view/WNHeader.tpl`: Added condition to render header only if deeplink is valid
*   `index.php`: Added logic to display deeplink header in the login page
*   `classes/class.deepLink.php`: Added logic to send user to welcome onboard page if the payment is already completed.
*   `classes/class.common.php`: Improved the logic for fetching request master history and request details history.
*   `classes/class.systemSetup.php`: Added payment expiry to system setup.
*   `classes/class.getFareCheckDetails.php`: Fixed an issue where the "Show More" button was not working correctly after modifying a request.
*   `classes/class.processRequest.php`: Added logic to remove through flights from the flight number when checking seat availability.

### 5. Key Functions/Methods:

*   **`class.tpl.holidayListInterface.php`**:
    *   `_getHolidaySkipData()`: Fetches holiday data and determines if a validity date falls on a holiday.
    *   `_validityCheckContract()`: Checks validity dates against holidays and non-business days, adjusting them as needed.
    *   `_reassignPaymentDetailsValueArr()`:To reconstruct paymentDetails array based on the paymentRequestDetails array
*   **`classes/class.processRequest.php`**:
    *   `_removeThroughFlights()`: To remove the through(via) flights from the flightNumber.

### 6. Implementation Guide:

To implement this feature in the latest branch, follow these steps:

1.  **Apply the patch**: Apply the provided patch file to your local branch.
2.  **Database Updates**: Execute the SQL statements in `database/WN_database.sql` to update the system settings.
3.  **Configuration**: Verify the configurations related to "controlViaFlights" in the system settings.
4.  **Code Review**: Thoroughly review the changes in `class.tpl.holidayListInterface.php`, paying close attention to the validity check logic.
5.  **Testing**:
    *   Create holiday lists for different countries and cities.
    *   Create group booking requests with validities that fall on holidays.
    *   Verify that the alert pop-up is displayed correctly.
    *   Test the autopilot policy to ensure that validity dates are automatically adjusted.
    *   Test the cloning functionality to ensure that cloned requests are handled correctly.
    *   Verify the functionality of the "Show More" button in fare check details.
    *   Test the dependency field validation alert message.
    *   Thoroughly test the deeplink functionality.
6.  **Deployment**: Deploy the updated code and database changes to your testing environment, followed by production.

### 7. Considerations:

*   **Edge Cases**: Consider edge cases such as holidays that span multiple days, different time zones, and leap years.
*   **Dependencies**: This feature depends on the Contract Manager module for adjusting validity dates.
*   **Performance**: The validity check logic in `class.tpl.holidayListInterface.php` could impact performance if not optimized.  Consider caching holiday data and optimizing database queries.
*   **Time Zones**: Ensure that time zone handling is consistent throughout the application, especially when calculating and adjusting validity dates.
*   **Payment logic**: Check the new payment logic in `class.tpl.holidayListInterface.php` for accuracy, especially the new function `_reassignPaymentDetailsValueArr()`.
*   **Via Flights**: Carefully review the changes in `class.processRequest.php` related to removing through flights, as this could affect seat availability checks.
*   **Deeplink**: Check the deeplink functionality for all scenarios.
*   **History**: Verify history functionality after changes.
```