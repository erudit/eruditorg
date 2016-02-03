$(document).ready(function() {
  Site();
});

function Site() {
  console.log("Site init!");
};

$(document).ready(function() {
  FoobarModule();
});

var FoobarModule = function() {
  console.log("Foobar init!");
};

$(document).ready(function() {
  Article();
});

function Article() {
  console.log("Article init!");
}
