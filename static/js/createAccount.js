import { toggleModal } from './errorModal.js';

async function genKey() {
    return await window.crypto.subtle.generateKey(
      {
        name: "RSA-OAEP",
        modulusLength: 2048,
        publicExponent: new Uint8Array([1, 0, 1]),
        hash: "SHA-256",
      },
      true,
      ["encrypt", "decrypt"]
    );
  }


  function encodeKey(key) {
    var str = String.fromCharCode.apply(null, new Uint8Array(key));
    var b64 = window.btoa(str);
    return b64;
  }

  async function exportPublicKey(key) {
    const publicKey = await crypto.subtle.exportKey("spki", key);
    return encodeKey(publicKey);
  }

  var idb = window.indexedDB.open("cs4455", 1);
  var db;

  idb.onerror = (event) => {
    console.log("Can't open indexedb");
  };

  idb.onupgradeneeded = (event) => {
    db = event.target.result;
    db.createObjectStore("dh-key", { keyPath: "id" });
    console.log("Upgraded");
  };

  idb.onsuccess = (event) => {
    db = event.target.result;
    console.log("db opened");
  };

document.getElementById('createAccountForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const username = event.target.username.value;
    const password = event.target.password.value;

    // Generate the key pair
    const keyPair = await genKey();

    // Save the key pair to IndexedDB
    let transaction = db.transaction(["dh-key"], "readwrite");
    let store = transaction.objectStore("dh-key");
    store.put({ id: 1, value: keyPair });

    // Export the public key to include in the form
    const publicKeyPem = await exportPublicKey(keyPair.publicKey);

    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    formData.append('publicKey', publicKeyPem);

    try {
        const response = await fetch('/createAccount', {
            method: 'POST',
            body: formData
        });
      
        if (response.ok) {
            window.location.replace("/user");
        } else {
            const errorData = await response.json();
            toggleModal('Error logging in: ' + errorData.error);
        }
    } catch (error) {
        toggleModal('Unknown error');
    }
});
