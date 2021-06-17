odoo.define("rich_payroll.rich_payroll_editor", function(require) {
    "use strict";
     
    var core = require("web.core");
    var dataset = require("web.data");
    var AbstractAction = require("web.AbstractAction");
    var Widget = require("web.Widget");
    var ajax = require('web.ajax');
    var _t = core._t;
    var QWeb = core.qweb;

    var rich_payroll_editor = AbstractAction.extend(
    {
        contentTemplate: "EmptyMainpage",
        
        
        custom_events: {
            my_test_button: "_myTestButton",
        },
        
        
        events: {
            'click button.js_my_test_button': "_myTestButton",
            'click #butt_write_garbage': "_writeMoreGarbage",
            'click #butt_write_dated_garbage': "_writeDatedGarbage",
        },
        
        
        _myTestButton: function (event)
        {
            alert("Ola");
        },
        
        
        _writeMoreGarbage: function (event)
        {
            var self = this;
            //alert(self.$("#garbage_box").text());
            var oldtext = self.$("#garbage_box").text();
            self.$("#garbage_box").text(oldtext + " garbage!")
        },
        
        
        _writeDatedGarbage: function (event)
        {
            var self = this;
            self._rpc({
                    model: "rich.payroll",
                    method: "heatbiit",
                    args: [],
                    //context: self.context,
                })
                .then(function (result) {
                    var oldtext = self.$("#garbage_box").text();
                    self.$("#garbage_box").text(oldtext + result)
                });

            
        },
        
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
    core.action_registry.add("rich_payroll_editor", rich_payroll_editor);
});
