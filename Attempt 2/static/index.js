function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
};

function getRecipeInfo(recipeId) {
  fetch("/get_recipe_info", {
    method: "POST",
    body: JSON.stringify({ recipeId: recipeId }),
  }).then((_res) => {
    window.location.href = "/recipe_info"
  });
};
