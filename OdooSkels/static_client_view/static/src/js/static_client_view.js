odoo.define("static_client_view.static_client_view", function(require) {
    "use strict";
     
    var core = require("web.core");
    var dataset = require("web.data");
    var AbstractAction = require("web.AbstractAction");
    var Widget = require("web.Widget");
    var _t = core._t;
    var QWeb = core.qweb;

    var static_client_view = AbstractAction.extend(
    {
        contentTemplate: "EmptyMainpage",
        
        
        //title: core._t("Rich Payroll Empty Page"),
        
        
        /*
        events: {
            'click .payslip-confirm' : 'payslip_confirm',
        },
        */
        /*
        start: function () {
            return $.when(
                new SearchForm(this).appendTo(this.$('.rich_editor_search_area')),
                new ResultForm(this).appendTo(this.$('.rich_editor_result_area'))
            );
        },
        */
    });
    core.action_registry.add("static_client_view", static_client_view);
});
    
