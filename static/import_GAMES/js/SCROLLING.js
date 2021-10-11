var rainbow = new Rainbow();
var best = 0;
rainbow.setSpectrum("#2ecc71","#ff9a42","#e74c3c");
rainbow.setNumberRange(0, 25000);
window.addEventListener('wheel', mouseWheelEvent);   
var lastSecond = [];

function mouseWheelEvent(e) {
  lastSecond.push({delta:Math.floor(Math.abs(e.deltaY)), timestamp: new Date().getTime()});
}
setInterval(function(){
  var pixelsPerSecond = displayLastSecond();
  if(pixelsPerSecond > best){
    best = pixelsPerSecond;
  }
  $(".pixels").text(numberWithCommas(pixelsPerSecond) + " pixels per second");
  console.log(makeGradient(pixelsPerSecond));
  $("body").css("background", "#" + rainbow.colourAt(pixelsPerSecond));
  $(".pixels").css("font-size",fontSize(pixelsPerSecond) + "px");
  if(pixelsPerSecond > 0){
    $(".headline").css("display", "none");
    $(".container").css("display", "block");
  }else{
    var headline = "Scroll as fast as you can!";
    if(best > 0){
      headline += "<div class='best'>Your best is "+ numberWithCommas(best)+" pixels per second</div>";
      $(".headline").css("height", "100px");
    }
    $(".headline").html(headline);
    $(".headline").css("display", "block");
    $(".container").css("display", "none");
  }
}, 50);

function displayLastSecond(){
  var now = new Date().getTime();
  var total = 0;
  var timestamps = 0;
  for(var x = 0; x < lastSecond.length; x++){
    if(now - lastSecond[x].timestamp <= 1000){
      total += lastSecond[x].delta;
      timestamps++;
    }else{
      lastSecond.splice(x, 1);
      x--;
    }
  }
  if(timestamps == 0){
    return 0;
  }
  return Math.round(total);
}
function fontSize(pps){
  return 32 + 20 * pps/25000;
}
function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
function makeGradient(pps){
  var color1 = rainbow.colourAt(pps);
  var color2 = rainbow.colourAt(pps+5000);
  return "radial-gradient(40% 40% at center, #" + color2 + ", #" + color1 + ")";
}