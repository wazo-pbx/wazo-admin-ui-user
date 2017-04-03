function create_list_table(list_url, get_url, delete_url) {
  var table_config = {
    ajax: list_url,
    columns: [
      { data: 'firstname' },
      { data: 'lastname' },
      { data: 'extension' },
      { data: 'provisioning_code' },
      { render: function(data, type, row) {
        return build_table_actions(get_url, delete_url, row.uuid);
      },
      },
    ]
  };
  create_table_serverside(table_config);
};
