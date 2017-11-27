$(document).ready(function() {
  create_list_table();
  init_add_available_extensions.call(this);

  $('.row-template').on("row:cloned", function(e, row) {
    init_add_available_extensions.call(row);
  });

  toggle_busy_destination_validator();
  $('#forwards-busy-enabled').change(toggle_busy_destination_validator);
  toggle_noanswer_destination_validator();
  $('#forwards-noanswer-enabled').change(toggle_noanswer_destination_validator);
  toggle_unconditional_destination_validator();
  $('#forwards-unconditional-enabled').change(toggle_unconditional_destination_validator);
});


function create_list_table() {
  var table_config = {
    columns: [{
        data: null,
        defaultContent: '',
        className: 'select-checkbox',
        orderable: false
      },
      { data: 'firstname' },
      { data: 'lastname' },
      { data: 'extension' },
      { data: 'provisioning_code' },
    ]
  };
  create_table_serverside(table_config);
};

function toggle_busy_destination_validator() {
    if ($('#forwards-busy-enabled').is(":checked")) {
      $('#forwards-busy-destination').attr('required', 'required');
    } else {
      $('#forwards-busy-destination').removeAttr('required');
    }
    $('form').validator('update');
    $('form').validator('validate');
}

function toggle_noanswer_destination_validator() {
    if ($('#forwards-noanswer-enabled').is(":checked")) {
      $('#forwards-noanswer-destination').attr('required', 'required');
    } else {
      $('#forwards-noanswer-destination').removeAttr('required');
    }
    $('form').validator('update');
    $('form').validator('validate');
}

function toggle_unconditional_destination_validator() {
    if ($('#forwards-unconditional-enabled').is(":checked")) {
      $('#forwards-unconditional-destination').attr('required', 'required');
    } else {
      $('#forwards-unconditional-destination').removeAttr('required');
    }
    $('form').validator('update');
    $('form').validator('validate');
}

function init_add_available_extensions(){
  $('.line-context', this).on("select2:select", function(e) {
    add_available_extensions.call(this);
  });
}


function add_available_extensions() {
  let extension_select = $(this).closest("tr").find(".line-extension")
  if (extension_select.length == 0) {
    extension_select = $(this).closest("form").find(".line-extension")
  }
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
