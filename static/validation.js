var i_width;
var i_height;
var ratio;
var img_name;

function togglePopover(id, flag){
  if (!flag){
    $(id).popover('show');
    $(id).removeClass("is-valid");
    $(id).addClass("is-invalid");
  }else{
    $(id).popover('hide');
    $(id).removeClass("is-invalid");
    $(id).addClass("is-valid");
  }

  $(id).popover('update');
}

$('#embroidery-width').on('propertychange input', function(event){
  var value = $('#embroidery-width').val();
  var isNum = $.isNumeric(value);

  if(isNum)
  {
    var width = Number.parseInt(value);
    if(width > 0 && width <= i_width){
      var height = width * ratio;

      $('#embroidery-height').val(Math.floor(height));
    }
  }
  togglePopover('#embroidery-width', isNum && width > 0 && width <= i_width);
});

$('#output-img-width').on('propertychange input', function(event){
  var value = $('#output-img-width').val();
  var isNum = $.isNumeric(value);

  if(isNum)
  {
    var width = Number.parseInt(value);
    if(width > 0){
      var height = width * ratio;

      $('#output-img-height').val(Math.floor(height));
    }
  }
  togglePopover('#output-img-width',  isNum && width > 0);

  var width = Number.parseInt(value);
});

$('#input-colors').on('propertychange input', function(event){
  var value = $('#input-colors').val();
  togglePopover('#input-colors', $.isNumeric(value));
});

function valXY(){
  var value = $('#input-xy').val();
  togglePopover('#input-xy', $.isNumeric(value));
}

$('#input-xy').on('propertychange input', function(event){
  valXY();
});

$('#help-symbols').on('mouseover', function(event){
  $('#help-symbols').tooltip('show');
});

$('#help-insert').on('mouseover', function(event){
  $('#help-insert').tooltip('show');
});

$('#input-xy-bool').on('propertychange input', function(event){
  var value = $('#input-xy-bool:checked').val();

  if(value){
    valXY();
    $('#input-xy').prop('disabled', false);
  }else{

    $('#input-xy').prop('disabled', true);
    togglePopover('#input-xy', true);
  }
});

$(function() {
  $('#button-options').click(function() {
      var e_width = $("#embroidery-width").val();
      var e_height = $("#embroidery-height").val();

      var o_width = $("#output-img-width").val();
      var o_height = $("#output-img-height").val();

      var symbols = $('#input-symbols:checked').val();

      var xy_bool = $('#input-xy-bool:checked').val();
      var xy_num = $('#input-xy').val();

      var colors = $('#input-colors').val();

      var insert = $('#input-insert:checked').val();

      var data = {
        'img_name' : img_name,
        'e_width' : e_width,
        'e_height' : e_height,
        'o_width' : o_width,
        'o_height' : o_height,
        'symbols' : symbols,
        'xy_bool' : xy_bool ? '1' : '0',
        'xy_num' : xy_num,
        'colors' : colors,
        'insert' : insert ? '1' : '0'
      };

      $.ajax({
          type: 'POST',
          url: '/gen_embroidery',
          data: JSON.stringify(data),
          contentType: "application/json; charset=utf-8",
          dataType: "json",
          async: false
      }).done(function(data, textStatus, jqXHR){
          window.location = data['url'];
      }).fail(function(data){
          alert('error!');
      });
  });
});


$(function() {
  $('#upload-file-btn').click(function() {
      var form_data = new FormData($('#upload-file')[0]);
      $.ajax({
          type: 'POST',
          url: '/upload_image',
          data: form_data,
          contentType: false,
          processData: false,
          async: false
      }).done(function(data, textStatus, jqXHR){
          $("#img-input-width").val(data['width']);
          $("#img-input-height").val(data['height']);
          img_name = data['name'];

          i_width = Number.parseInt(data['width']);
          i_height = Number.parseInt(data['height']);
          ratio = i_width / i_height;

          $("#modal").modal('show');
      }).fail(function(data){
          alert('error!');
      });
  });
});
