var upd_id = setInterval(update, 5000);
function update() {
  if (filename !== '') {
    $.ajax({
      type: "POST",
      url: "/process",
      dataType: 'json',
      contentType: 'application/json;charset=UTF-8',
      data: JSON.stringify({'code': filename}),
      success: function(data) {
        if (data.status === 'founded') {
          clearInterval(upd_id);
          location.href = '/process?code=' + filename;
        }
      }
    });
  }
}