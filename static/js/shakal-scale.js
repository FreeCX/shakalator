function format() {
  var result = "";
  x = parseInt(scale_value.value);
  if (x >= 0 && x < 10) {
    result = "Ультрашакализм";
  } else if (x >= 10 && x < 20) {
      result = "10/10 шакалов";
  } else if (x >= 20 && x < 30) {
      result = "9/10 шакалов";
  } else if (x >= 30 && x <= 50) {
    result = "8/10 шакалов";
  } else if (x >= 60 && x <= 70) {
    result = "Умеренный шакализм";
  } else if (x >= 80 && x <= 90) {
    result = "Стандартный шакализм";
  } else if (x >= 100 && x <= 150) {
    result = "Умеренное качество";
  } else if (x >= 160 && x <= 200) {
    result = "Нормальное качество";
  }
  scale_text.innerHTML = result;
}