$(document).ready(function() {
  create_list_table();
  init_add_available_extensions.call(this);

  $('.row-template').on("row:cloned", function(e, row) {
    init_add_available_extensions.call(row);
  });

  $('.row-line').each(function(e, row) {
    add_available_extensions.call(row);
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
    columns: [
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
  add_available_extensions()
}


function add_available_extensions() {
  let extension_select, context_select

  if ($('.row-template').length == 0) {
    extension_select = $(".line-extension")
    context_select = $(".line-context")
  } else {
    extension_select = $(this).closest("tr").find(".line-extension")
    context_select = $(this).closest("tr").find(".line-context")
    if (extension_select.length == 0) {
      extension_select = $(this).closest("form").find(".line-extension")
    }
  }

  let ajax_url = $(extension_select).attr('data-available_extension_href')
  if (! ajax_url || ! context_select) {
    return;
  }

  extension_select.select2({
    theme: 'bootstrap',
    ajax: {
      url: ajax_url,
      data: function (params) {
        return {
          term: params.term,
          context: context_select.val()
        }
      }
    }
  });
}
