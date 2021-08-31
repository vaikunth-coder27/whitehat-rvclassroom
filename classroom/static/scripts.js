function toggle_menu() {
    var x = document.getElementById("menubar");
    if (x.style.display === "block") {
        x.style.animation = "fadeout 1s linear 1 forwards";
        x.style.display = "none";
    } 
    else {
        x.style.animation = "fadein 1s linear 1 forwards";
        x.style.display = "block";
    }
  }

function toggle_menu_right() {
    var x = document.getElementById("right-menu");
    if (x.style.display === "block") {
        x.style.animation = "fadeout 0.5s linear 1 forwards";
        x.style.display = "none";
    } 
    else {
        x.style.animation = "fadein 0.5s linear 1 forwards";
        x.style.display = "block";
    }
}