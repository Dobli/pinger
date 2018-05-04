/*
 * Add a date picker to a text input field (native or jquery)
 *
 * @param domId - id of text field dom element
 * @param selectionHandler - function to handle date changes
 */
function addDatepickerToTextInput(domId, selectionHandler){
    $("input[type=date]").each(function() {
        // if date input is not supported use jquery date picker, else native date
        if  (this.type != 'date' ) {
            $(this).datepicker({
                onSelect: selectionHandler,
                dateFormat: "yy-mm-dd"
            }).datepicker("setDate", new Date());
        } else {
            $(this).change(selectionHandler);
            $(this).get(0).valueAsDate = new Date();
        }
    });
}

/*
 * Populate a selector with pool options, optionally add a selection change handler
 *
 * @param domId - Id of selection dom element
 * @param pools - List of pools to add to selector
 * @param selectionHandler - Function to call when selection changes
 */
function setPoolList(domId, pools, selectionHandler){
    pools.forEach(function (element, index) {
        $( '#'+domId ).append(new Option(element.room_no, element.pk))
    });
    $( '#'+domId ).parent().addClass('is-dirty');
    $( '#'+domId ).change(selectionHandler);
};

/**
 * Populate a mdl list with pool entries and switches
 *
 * @param domId - id of mdl list dom element to populate
 * @param pools - list of pools to put into the lsit
 */
function setPoolListMdl(domId, pools){
    ul = $ ( '#'+domId );
    pools.forEach(function (element, index) {
        var index = ul.children.length + 1;
        // add mdl specific list containers
        var li = document.createElement("li");
        li.setAttribute("class", "mdl-list__item");

        // add mdl styled switch
        var checkSpan = document.createElement("label");
        checkSpan.setAttribute("class", "mdl-switch mdl-js-switch mdl-js-ripple-effect");
        checkSpan.setAttribute("for", "pool-"+element.pk);
        var checkBox = document.createElement("input");
        checkBox.setAttribute("name", "pool_ids");
        checkBox.setAttribute("id", "pool-"+element.pk);
        checkBox.setAttribute("value", element.pk)
        checkBox.setAttribute("class", "mdl-switch__input");
        checkBox.setAttribute("type", "checkbox");
        var checkBoxText = document.createElement("label");
        checkBoxText.setAttribute("class", "mdl-switch__label")
        checkBoxText.appendChild(document.createTextNode(element.room_no))
        checkSpan.appendChild(checkBox);
        checkSpan.appendChild(checkBoxText);

        // upgarde elements to use material design classes
        componentHandler.upgradeElement(checkSpan);

        // append text and checkBox to list
        li.appendChild(checkSpan);
        ul.append(li);

    });
};


// API functions
// HINT: set corresponding endpoints in the base.html

/**
 * Call API endpoint to fet list of pools, execute callback if present on success
 *
 * @param poolHandlerCallback - Callback to execute on success, able to handle pool list
 */
function getPoolListData(poolHandlerCallback){
    var poolUrl = endpoint_pools()
    // Retrive list of pools
    $.ajax({
        method: "GET",
        url: poolUrl,
        success: function(data){
            // call callback with pool data
            poolHandlerCallback(data.pools)
        },
        error: function(error_data){
            console.log("Error: could not retrieve Pool List")
            console.log(error_data)
        }
    });
}

/**
 * Retrive chart data of a pool for today and call successHandler with
 * received data, on error a console log will be shown
 *
 * @param poolId - pool to retreive data for
 * @param successHandler - function to call on success, gets chartData as parameter
 */
function getChartData(poolId, successHandler){
    var poolUrl = endpoint_chart_data(poolId)
    $.ajax({
        method: "GET",
        url: poolUrl,
        success: successHandler,
        error: function(error_data){
            console.log("error")
            console.log(error_data)
        }
    });
};

/**
 * Retrive chart data of a pool for a given date and call successHandler with
 * received data, on error a console log will be shown
 *
 * @param poolId - pool to retreive data for
 * @param year - year to use
 * @param month - month to use
 * @param day - day to use
 * @param successHandler - function to call on success, gets chartData as parameter
 */
function getChartDateData(poolId, year, month, day, successHandler){
    var poolUrl = endpoint_chart_date_url(poolId, year, month, day)
    $.ajax({
        method: "GET",
        url: poolUrl,
        success: successHandler,
        error: function(error_data){
            console.log("error")
            console.log(error_data)
        }
    });
};

/**
 * Retrive data of a pcs currently online in a pool and call successHandler with
 * received data, on error a console log will be shown
 *
 * @param poolId - pool to retreive data for
 * @param successHandler - function to call on success, gets chartData as parameter
 */
function getCurrentlyOnline(poolId, successHandler){
    var poolUrl = endpoint_chart_data_online_pcs(poolId)
    $.ajax({
        method: "GET",
        url: poolUrl,
        success: successHandler,
        error: function(error_data){
            console.log("error")
            console.log(error_data)
        }
    });
};
