define(['knockout'], function (ko) {
    var NodeModel = function(source, datatypelookup) {
        var self = this;
        self.datatypelookup = datatypelookup;

        self.parse(source);

        self.json = ko.computed(function() {
            return JSON.stringify(_.extend(JSON.parse(self._node()), {
                name: self.name()
            }))
        });

        self.dirty = ko.computed(function() {
            return self.json() !== self._node();
        });
    };

    NodeModel.prototype = {
        constructor: NodeModel,

        parse: function(source) {
            var self = this;
            self._node = ko.observable(JSON.stringify(source));
            self.selected = ko.observable(false);
            self.filtered = ko.observable(false);
            self.editing = ko.observable(false);
            self.name = ko.observable(source.name);

            self.nodeid = source.nodeid;
            self.datatype = source.datatype;
            self.iconclass = self.datatypelookup[source.datatype];
            self.istopnode = source.istopnode;
            self.ontologyclass = source.ontologyclass;
        },

        reset: function () {
            self.parse(JSON.parse(self._node()), self);
        }
    };

    return NodeModel;
});
