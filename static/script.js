
document.querySelector('#tweetUrl').addEventListener('change', e=>{
  const tweet = document.querySelector('#tweet');
  tweet.innerHTML = '';
  const tweetUrl = e.currentTarget;
  const tweetId = tweetUrl.value.match(/https:\/\/twitter.com\/\w+\/status\/(\d+)/)[1];
  document.querySelector('#tweetId').value = tweetId;
  twttr.widgets.createTweet(tweetId, tweet, {conversation: false}).then(e=>{
    const pinSubmit = document.querySelector('#pinSubmit');
    pinSubmit.disabled = !e || document.querySelector('#loginStatus').value == "false";
  });
});


document.querySelector('#pinForm').addEventListener('submit', e=>{
  e.preventDefault();
  const tweetUrl = document.querySelector('#tweetUrl');
  if (confirm(`このツイートをプロフィールに固定しますか?\n${tweetUrl.value}`)) {
    const form = document.querySelector('#pinForm');
    fetch('/pin_tweet', {method:'post', body:new FormData(form)}).then(r=>{
      if (r.ok) {
        r.json().then(console.log);
        alert(`${r.status}: ツイートを固定しました`);
      } else {
        r.json().then(console.error);
        alert(`${r.status}: エラーが発生しました`);
      }
    });
  };
});