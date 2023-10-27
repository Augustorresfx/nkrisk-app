const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
const htmlElement = document.getElementById("colorMode");

if (prefersDarkMode) {
  htmlElement.setAttribute("data-bs-theme", "dark");
} else {
  htmlElement.setAttribute("data-bs-theme", "light");
}


document.getElementById("colorModeButton").addEventListener("click", function() {
  // Verificamos el tema actual y cambiamos al tema opuesto
  if (htmlElement.getAttribute("data-bs-theme") === "light") {
      htmlElement.setAttribute("data-bs-theme", "dark");
  }
  else if(htmlElement.getAttribute("data-bs-theme") === "auto"){
      htmlElement.setAttribute("data-bs-theme", "dark");
  }
  else{
      htmlElement.setAttribute("data-bs-theme", "light");
  }
});