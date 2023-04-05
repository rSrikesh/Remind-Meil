const info = document.getElementById('info')
const i = document.getElementById('email')
const p = document.getElementById('password')
const btn = document.getElementById('btn')

btn.addEventListener('click', () => {
  const email = i.value
  const password = p.value
  let data = {
    name: email,
    password: password
  }
  fetch(`http://127.0.0.1:5001/data`,{
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  }).then(response => {
    return response.json(); 
  }).then(json => {
    json.forEach(element => {
      const item = document.createElement('div');
      item.classList.add('item');
      item.innerHTML = `<span>${element.event}<span>`;
      info.appendChild(item);
      console.log(element);
    });
  })
  // .then ((text)=>{
  //   info.innerHTML = text;
  // })
  .catch(e=>{
    console.log(e);
  })

})
