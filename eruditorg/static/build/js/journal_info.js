!function(t){var e={};function n(i){if(e[i])return e[i].exports;var r=e[i]={i:i,l:!1,exports:{}};return t[i].call(r.exports,r,r.exports,n),r.l=!0,r.exports}n.m=t,n.c=e,n.d=function(t,e,i){n.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:i})},n.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},n.t=function(t,e){if(1&e&&(t=n(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var i=Object.create(null);if(n.r(i),Object.defineProperty(i,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var r in t)n.d(i,r,function(e){return t[e]}.bind(null,r));return i},n.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return n.d(e,"a",e),e},n.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},n.p="",n(n.s=393)}({1:function(t,e,n){"use strict";function i(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}var r=function(){function t(e){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t),this.controllers=void 0===e?{}:e}var e,n,r;return e=t,(n=[{key:"execAction",value:function(t,e){""!==t&&this.controllers[t]&&"function"==typeof this.controllers[t][e]&&this.controllers[t][e]()}},{key:"init",value:function(){if(document.body){var t=document.body,e=t.getAttribute("data-controller"),n=t.getAttribute("data-action");e&&(this.execAction(e,"init"),this.execAction(e,n))}}}])&&i(e.prototype,n),r&&i(e,r),t}();e.a=r},393:function(t,e,n){"use strict";n.r(e);var i=n(1);function r(t,e){for(var n=0;n<e.length;n++){var i=e[n];i.enumerable=i.enumerable||!1,i.configurable=!0,"value"in i&&(i.writable=!0),Object.defineProperty(t,i.key,i)}}var o=function(){function t(){!function(t,e){if(!(t instanceof e))throw new TypeError("Cannot call a class as a function")}(this,t)}var e,n,i;return e=t,(n=[{key:"init",value:function(){$("#id_languages").select2(),this.contributor_fieldset=$('fieldset[name="contributors"]'),this.set_formset_state()}},{key:"set_formset_state",value:function(){var t=this;$("#button-add-contributor").off("click").on("click",(function(e){e.stopPropagation(),t.add_contributor(),t.set_formset_state()})),$("button[data-action='delete']").off("click").on("click",(function(e){e.stopPropagation();var n=$(this).parent().parent().data("object");t.delete_contributor($("div[data-object='"+n+"']")),t.set_formset_state()}));var e=$(this.contributor_fieldset).children('div[class="row"][id]');$(e).each((function(e){$(this).attr("data-object",e),$(t.get_inputs($(this))).each((function(t){var n=$(this).attr("id").replace(/\d+/,e),i=$(this).attr("name").replace(/\d/,e);$(this).attr("id",n),$(this).attr("name",i)}))}));var n=$(this.contributor_fieldset).children('div[class="row"][id]').length,i=$('input[type="hidden"][name$="id"][value]').length;$("#id_contributor_set-TOTAL_FORMS").val(n),$("#id_contributor_set-INITIAL_FORMS").val(i)}},{key:"clear_inputs",value:function(t){var e=this.get_inputs(t);$(e).not('[id$="journal_information"]').not('[id$="id"]').val("")}},{key:"get_inputs",value:function(t){return $(t).find("input").add($(t).find("select"))}},{key:"add_contributor",value:function(){var t=$('fieldset[name="contributors"] > div[class="row"]:last'),e=$(t).clone();this.clear_inputs(e),$(t).after(e)}},{key:"delete_contributor",value:function(t){var e=$(t).find('[id$="name"]').val(),n=window.confirm("Êtes-vous certain de vouloir retirer "+e+" de la liste des collaborateurs?"),i=$(this.contributor_fieldset).data("form-url");if(n){var r=$(t).find('[id$="id"]').val();if(""!==r){var o=this;$.ajax({type:"POST",url:i,data:{contributor_id:r},success:function(){o.clear_inputs(t),$(this.contributor_fieldset).children('div[class="row"][id]').length>1&&$(t).hide()}})}1==$(this.contributor_fieldset).children('div[class="row"][id]').length?this.clear_inputs(t):$(t).remove()}}}])&&r(e.prototype,n),i&&r(e,i),t}();$(document).ready((function(){new i.a({"userspace:journalinformation:update":new o}).init()}))}});