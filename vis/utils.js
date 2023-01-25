

function linearInterp(value, rangeMin, rangeMax, outMin, outMax, exponent = 0.4) {
    // returns a value between outMin and outMax depending on where value lies between rangeMin and rangeMax; truncates
    if (rangeMin != rangeMax) {
      const where = (value - rangeMin) / (rangeMax - rangeMin); // 0-1
      return outMin + Math.pow(where, exponent) * (outMax - outMin);
    }
    return 1;
  }
  
  
  function HSLToRGB(h, s, l) {
    // h is 0-360, s is 0-100, l is 0-100
    s /= 100;
    l /= 100;
  
    let c = (1 - Math.abs(2 * l - 1)) * s,
      x = c * (1 - Math.abs(((h / 60) % 2) - 1)),
      m = l - c / 2,
      r = 0,
      g = 0,
      b = 0;
  
    if (0 <= h && h < 60) {
      r = c;
      g = x;
      b = 0;
    } else if (60 <= h && h < 120) {
      r = x;
      g = c;
      b = 0;
    } else if (120 <= h && h < 180) {
      r = 0;
      g = c;
      b = x;
    } else if (180 <= h && h < 240) {
      r = 0;
      g = x;
      b = c;
    } else if (240 <= h && h < 300) {
      r = x;
      g = 0;
      b = c;
    } else if (300 <= h && h < 360) {
      r = c;
      g = 0;
      b = x;
    }
    r = Math.round((r + m) * 255);
    g = Math.round((g + m) * 255);
    b = Math.round((b + m) * 255);
  
    return [r, g, b];
  }
  function RGBToHex(r, g, b) {
    r = r.toString(16);
    g = g.toString(16);
    b = b.toString(16);
  
    if (r.length == 1) r = '0' + r;
    if (g.length == 1) g = '0' + g;
    if (b.length == 1) b = '0' + b;
  
    return '#' + r + g + b;
  }
  
  function HSLtoHex(h, s, l) {
    // converts (0-360, 0-100, 0-100) to hex color
    const t = HSLToRGB(h, s, l);
    return RGBToHex(t[0], t[1], t[2]);
  }
  
  function gen_color(
    value_in_unit_interval,
    min_luminence = 0.6,
    max_luminence = 1,
    min_saturation = 0.4,
    max_saturation = 1,
    min_hue = 90,
    max_hue = 270
  ) {
    const hue = min_hue + Math.floor(Math.random() * (max_hue - min_hue)); // linearInterp(weight, 0, 1, 0, 180); //
    const lumin = linearInterp(value_in_unit_interval, 0, 1, min_luminence, max_luminence, 1);
    const saturation = linearInterp(value_in_unit_interval, 0, 1, min_saturation, max_saturation, 1);
    return HSLtoHex(hue, saturation * 100, lumin * 100);
  }
  
  
  
  function hue_interp(minn, maxx) {
    maxx = minn > maxx ? maxx + 360 : maxx;
    return;
  }
  