import { toggleModal } from './errorModal.js';
//set up section
var idb = window.indexedDB.open("cs4455", 1);
let db;

idb.onerror = (event) => {
  console.log("Can't open indexedb");
};

idb.onsuccess = (event) => {
  db = event.target.result;
  console.log("db opened");
};

async function getPrivateKey() {
  return new Promise((resolve, reject) => {
    let transaction = db.transaction(["dh-key"], "readonly");
    let store = transaction.objectStore("dh-key");
    let request = store.get(1);

    request.onsuccess = (event) => {
      if (request.result) {
        resolve(request.result.value.privateKey);
      } else {
        reject("Private key not found in IndexedDB");
      }
    };

    request.onerror = (event) => {
      reject("Error retrieving private key from IndexedDB");
    };
  });
}

//upload section
async function encryptFile(file) {
  const symmetricKey = await window.crypto.subtle.generateKey(
    { name: "AES-GCM", length: 256 },
    true,
    ["encrypt", "decrypt"]
  );

  const iv = window.crypto.getRandomValues(new Uint8Array(12));
  const encryptedContent = await window.crypto.subtle.encrypt(
    { name: "AES-GCM", iv: iv },
    symmetricKey,
    await file.arrayBuffer()
  );

  const exportedSymmetricKey = await window.crypto.subtle.exportKey("raw", symmetricKey);

  return {
    encryptedContent: new Uint8Array(encryptedContent),
    iv: iv,
    symmetricKey: exportedSymmetricKey
  };
}

async function encryptSymmetricKey(publicKey, symmetricKey) {
  const importedPublicKey = await window.crypto.subtle.importKey(
    "spki",
    Uint8Array.from(atob(publicKey), c => c.charCodeAt(0)),
    { name: "RSA-OAEP", hash: "SHA-256" },
    false,
    ["encrypt"]
  );

  const encryptedSymmetricKey = await window.crypto.subtle.encrypt(
    { name: "RSA-OAEP" },
    importedPublicKey,
    symmetricKey
  );

  return new Uint8Array(encryptedSymmetricKey);
}

async function handleUpload(event) {
  event.preventDefault();

  const fileInput = document.getElementById("file");
  const receiverSelect = document.getElementById("receiver");
  const file = fileInput.files[0];
  const receiver = receiverSelect.value;

  if (!file || !receiver) {
    toggleModal("Please select a file and receiver.");
    return;
  }

  try {
    const response = await fetch(`/getPublicKey?user=${receiver}`);
    const data = await response.json();

    if (data.error) {
      throw new Error(data.error);
    }

    const publicKey = data.publicKey;
    const { encryptedContent, iv, symmetricKey } = await encryptFile(file);
    const encryptedSymmetricKey = await encryptSymmetricKey(publicKey, symmetricKey);

    const formData = new FormData();
    formData.append("file", new Blob([encryptedContent], { type: file.type }), file.name);
    formData.append("iv", btoa(String.fromCharCode.apply(null, iv)));
    formData.append("encryptedSymmetricKey", btoa(String.fromCharCode.apply(null, encryptedSymmetricKey)));
    formData.append("select", receiver);
    const uploadResponse = await fetch("/upload", {
      method: "POST",
      body: formData
    });

    if (uploadResponse.ok) {
      alert("File uploaded successfully.");
    } else {
      toggleModal("Error uploading file.");
    }
  } catch (error) {
    console.error("Error during file upload:", error);
  }
}

document.getElementById("uploadForm").addEventListener("submit", handleUpload);

//download section
async function decryptSymmetricKey(privateKey, encryptedSymmetricKey) {
  const encryptedKeyBuffer = base64ToArrayBuffer(encryptedSymmetricKey);
  const decryptedKey = await window.crypto.subtle.decrypt(
    {name: "RSA-OAEP"},
    privateKey,
    encryptedKeyBuffer
  );

  return new Uint8Array(decryptedKey);
}

function base64ToArrayBuffer(base64) {
  const binaryString = window.btoa(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

async function decryptFile(encryptedFileContentBase64, symmetricKeyBase64, ivBase64) {
  const symmetricKeyArrayBuffer = base64ToArrayBuffer(symmetricKeyBase64);
  const ivArrayBuffer = base64ToArrayBuffer(ivBase64);
  const encryptedFileArrayBuffer = base64ToArrayBuffer(encryptedFileContentBase64)
  const importedSymmetricKey = await window.crypto.subtle.importKey(
    "raw",
    symmetricKeyArrayBuffer,
    { name: "AES-GCM" },
    true,
    ["decrypt"]
  )
  const decryptedContent = await window.crypto.subtle.decrypt(
    { name: "AES-GCM", iv: new Uint8Array(ivArrayBuffer) },
    importedSymmetricKey,
    encryptedFileArrayBuffer
  )
  return new Uint8Array(decryptedContent);
}

async function downloadFile(id) {
  try {
    const privateKey = await getPrivateKey();
    const keyResponse = await fetch(`/getEncryptedSymmetricKey?id=${id}`);
    const keyData = await keyResponse.json();
    if (keyData.error) {
      throw new Error(keyData.error);
    }
    const encryptedSymmetricKey = keyData.symmetricKey;
    const iv = keyData.iv;
    const symmetricKey = await decryptSymmetricKey(privateKey, encryptedSymmetricKey);
    const decryptedIv = new Uint8Array(atob(iv).split('').map(char => char.charCodeAt(0)))
    const fileResponse = await fetch(`/downloadEncryptedFile?file=${fileName}`);
    const fileData = await fileResponse.json();
    if (fileData.error) {
      throw new Error(fileData.error);
    }
    const encryptedFileContent = fileData.fileContent
    const decryptedContent = await decryptFile(encryptedFileContent, symmetricKey, decryptedIv);
    const blob = new Blob([decryptedContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;  
    a.download = fileName; // Fix: Add file name for download
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    toggleModal('Error downloading file.');
    console.error('Error during decryption:', error);
  }
}

document.getElementById('downloadMe').addEventListener('click', (event) => {
  downloadFile(event.target.value);
});