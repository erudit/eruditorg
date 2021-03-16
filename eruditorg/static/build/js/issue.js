!function(t){var e={};function n(o){if(e[o])return e[o].exports;var a=e[o]={i:o,l:!1,exports:{}};return t[o].call(a.exports,a,a.exports,n),a.l=!0,a.exports}n.m=t,n.c=e,n.d=function(t,e,o){n.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:o})},n.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},n.t=function(t,e){if(1&e&&(t=n(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var o=Object.create(null);if(n.r(o),Object.defineProperty(o,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var a in t)n.d(o,a,function(e){return t[e]}.bind(null,a));return o},n.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return n.d(e,"a",e),e},n.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},n.p="",n(n.s=77)}({0:function(t,e,n){"use strict";function o(t,e){for(var n=0;n<e.length;n++){var o=e[n];o.enumerable=o.enumerable||!1,o.configurable=!0,"value"in o&&(o.writable=!0),Object.defineProperty(t,o.key,o)}}var a=function(){function t(e){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.controllers=void 0===e?{}:e}var e,n,a;return e=t,(n=[{key:"execAction",value:function(t,e){""!==t&&this.controllers[t]&&"function"==typeof this.controllers[t][e]&&this.controllers[t][e]()}},{key:"init",value:function(){if(document.body){var t=document.body,e=t.getAttribute("data-controller"),n=t.getAttribute("data-action");e&&(this.execAction(e,"init"),this.execAction(e,n))}}}])&&o(e.prototype,n),a&&o(e,a),t}();e.a=a},3:function(t,e,n){"use strict";function o(){return(o=Object.assign||function(t){for(var e=1;e<arguments.length;e++){var n=arguments[e];for(var o in n)Object.prototype.hasOwnProperty.call(n,o)&&(t[o]=n[o])}return t}).apply(this,arguments)}function a(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}function i(t,e){for(var n=0;n<e.length;n++){var o=e[n];o.enumerable=o.enumerable||!1,o.configurable=!0,"value"in o&&(o.writable=!0),Object.defineProperty(t,o.key,o)}}var r=function(){function t(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{};a(this,t);var n={documentAddDataAttribute:"citation-save",documentRemoveDataAttribute:"citation-remove",documentButtonSelector:"[data-citation-list-button]",documentIdDataAttribute:"document-id",documentIsSavedDataAttribute:"is-in-citation-list"};this.options=o(n,e),this.addButtonSelector="[data-"+this.options.documentAddDataAttribute+"]",this.removeButtonSelector="[data-"+this.options.documentRemoveDataAttribute+"]"}var e,n,r;return e=t,(n=[{key:"save",value:function(t){var e=this,n=t.data(this.options.documentIdDataAttribute),o=t.attr("id");$.ajax({type:"POST",url:Urls["public:citations:add_citation"](),data:{document_id:n}}).done((function(){t.data(e.options.documentIsSavedDataAttribute,!0),$("[data-"+e.options.documentAddDataAttribute+'="#'+o+'"]').hide(),$("[data-"+e.options.documentRemoveDataAttribute+'="#'+o+'"]').show()}))}},{key:"remove",value:function(t){var e=this,n=t.data(this.options.documentIdDataAttribute),o=t.attr("id");$.ajax({type:"POST",url:Urls["public:citations:remove_citation"](),data:{document_id:n}}).done((function(){t.data(e.options.documentIsSavedDataAttribute,!1),$("[data-"+e.options.documentAddDataAttribute+'="#'+o+'"]').show(),$("[data-"+e.options.documentRemoveDataAttribute+'="#'+o+'"]').hide()}))}},{key:"init",value:function(){var t=this;$(this.addButtonSelector).on("click",(function(e){var n=$($(e.currentTarget).data(t.options.documentAddDataAttribute));t.save(n),e.preventDefault()})),$(this.removeButtonSelector).on("click",(function(e){var n=$($(e.currentTarget).data(t.options.documentRemoveDataAttribute));t.remove(n),e.preventDefault()})),$("[data-"+this.options.documentIdDataAttribute+"]").each((function(e,n){var o=$(n).attr("id");1==$(n).data(t.options.documentIsSavedDataAttribute)?($("[data-"+t.options.documentAddDataAttribute+'="#'+o+'"]').hide(),$("[data-"+t.options.documentRemoveDataAttribute+'="#'+o+'"]').show()):($("[data-"+t.options.documentAddDataAttribute+'="#'+o+'"]').show(),$("[data-"+t.options.documentRemoveDataAttribute+'="#'+o+'"]').hide())}))}}])&&i(e.prototype,n),r&&i(e,r),t}();e.a=r},77:function(t,e,n){n(96),t.exports=n(78)},78:function(t,e,n){},96:function(t,e,n){"use strict";n.r(e);var o=n(0),a=n(3),i={init:function(){this.saved_citations=new a.a,this.saved_citations.init()}};$(document).ready((function(){new o.a({"public:journal:issue_detail":i}).init()}))}});