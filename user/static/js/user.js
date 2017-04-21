function create_list_table() {
  var table_config = {
    columns: [
      { data: 'firstname' },
      { data: 'lastname' },
      { data: 'extension' },
      { data: 'provisioning_code' },
    ]
  };
  create_table_serverside(table_config);
};


$(document).ready(function() {
  create_list_table();
  init_add_available_extensions.call(this);

  $('.row-template').on("row:cloned", function(e, row) {
    init_add_available_extensions.call(row);
  });
});


function init_add_available_extensions(){
  $('.line-context', this).on("select2:select", function(e) {
    add_available_extensions.call(this);
  });
}


function add_available_extensions() {
  let extension_select = $(this).closest("tr").find(".line-extension")
  let ajax_url = $(extension_select).attr('data-available_extension_href')
  if (! ajax_url) {
    return;
  }

  $.ajax({
    url: ajax_url,
    data: {context: $(this).val()},
    success: function(response) {
      for (i = 0; i < response.results.length; i++) {
        extension_select.append($("<option></option>")
                                .attr("value", response.results[i].id)
                                .text(response.results[i].text));
      }
    }
  });
}
