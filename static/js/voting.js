/*function vote(type, postId) {
  fetch(`/${type}/${postId}`, {
    method: 'POST'
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById(`upvotes-${postId}`).innerText = data.upvotes;
    document.getElementById(`downvotes-${postId}`).innerText = data.downvotes;
  })
  .catch(err => console.error("Vote error:", err));
}*/
