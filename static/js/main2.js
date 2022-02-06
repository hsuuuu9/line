var array = [];
var newArray = [];
var count = 1;
function random(array, num) {
  var a = array;
  var t = [];
  var r = [];
  var l = a.length;
  var n = num < l ? num : l;
  while (n-- > 0) {
    var i = Math.random() * l | 0;
    r[n] = t[i] || a[i];
    --l;
    t[i] = t[l] || a[l];
  }
  return r;
}

for (var i = 0; i < 77; i++) {
  array.push(i);
}
newArray = random(array, 25);
for (var n = 1; n < 26; n++) {
  var tmp = document.getElementById("n"+(Number(newArray[n-1])+1));
  tmp.innerHTML = "<p onclick='touch()'>"+n+"</p>";
}
function touch(){
  if(count == 1){
    const startTime = performance.now();

  }
  if(count == event.target.innerHTML){
    event.target.style.display = "none";
    count += 1;

  }else if(count == 25){
    const endTime = performance.now();

  }
}
