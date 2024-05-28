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

async function getSigningKey() {
  return new Promise((resolve, reject) => {
    let transaction = db.transaction(["dh-key"], "readonly");
    let store = transaction.objectStore("dh-key");
    let request = store.get(2);

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

  const signingKey = await getSigningKey();
  console.log(typeof signingKey);

  const iv = window.crypto.getRandomValues(new Uint8Array(12));
  const encryptedContent = await window.crypto.subtle.encrypt(
    { name: "AES-GCM", iv: iv },
    symmetricKey,
    await file.arrayBuffer()
  );

  const exportedSymmetricKey = await window.crypto.subtle.exportKey("raw", symmetricKey);
  const signature = await signFile(encryptedContent, signingKey.privateKey);

  return {
    encryptedContent: new Uint8Array(encryptedContent),
    signature: new Uint8Array(signature),
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

async function signFile(file, signingKey){
  let signature = await window.crypto.subtle.sign(
    {
      name: "ECDSA",
      hash: { name: "SHA-384" },
    },
    signingKey,
    file,
  );
  return signature;
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
    const { encryptedContent, signature, iv, symmetricKey } = await encryptFile(file);
    const encryptedSymmetricKey = await encryptSymmetricKey(publicKey, symmetricKey);

    const formData = new FormData();
    formData.append("file", new Blob([encryptedContent], { type: file.type }), file.name);
    formData.append("signedFile", btoa(signature));
    formData.append("iv", arrayBufferToBase64(iv));
    formData.append("encryptedSymmetricKey", arrayBufferToBase64(encryptedSymmetricKey));
    formData.append("select", receiver);
    const uploadResponse = await fetch("/upload", {
      method: "POST",
      body: formData
    });

    console.log(uploadResponse);

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

// Convert Uint8Array to Base64 String
function arrayBufferToBase64(buffer) {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

// Convert Base64 String to ArrayBuffer
function base64ToArrayBuffer(base64) {
  const binaryString = window.atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

async function blobToArrayBuffer(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsArrayBuffer(blob);
  });
}


//download section
async function decryptSymmetricKey(privateKey, encryptedSymmetricKey) {
  const encryptedKeyBuffer = base64ToArrayBuffer(encryptedSymmetricKey);
  const decryptedKey = await window.crypto.subtle.decrypt(
    { name: "RSA-OAEP" },
    privateKey,
    encryptedKeyBuffer
  );

  return new Uint8Array(decryptedKey);
}

async function decryptFile(encryptedFileContent, symmetricKey, iv) {
  const importedSymmetricKey = await window.crypto.subtle.importKey(
    "raw",
    symmetricKey,
    { name: "AES-GCM" },
    true,
    ["decrypt"]
  )
  const decryptedContent = await window.crypto.subtle.decrypt(
    { name: "AES-GCM", iv: iv },
    importedSymmetricKey,
    encryptedFileContent
  )
  return new Uint8Array(decryptedContent);
}

async function verifyFile(file, signature, publicKey){
  let isVerified = await window.crypto.subtle.verify(
    {
      name: "ECDSA",
      hash: { name: "SHA-384" },
    },
    publicKey,
    signature,
    file
  );

  return isVerified;
}

async function downloadFile(id, fileName) {
  try {
    const privateKey = await getPrivateKey();
    const keyResponse = await fetch(`/getEncryptedSymmetricKey?id=${id}`);
    const keyData = await keyResponse.json();
    if (keyData.error) {
      throw new Error(keyData.error);
    }
    const encryptedSymmetricKey = keyData.symmetricKey;
    const iv = keyData.iv;
    console.log(encryptedSymmetricKey);
    console.log(iv);
    const symmetricKey = await decryptSymmetricKey(privateKey, encryptedSymmetricKey);
    console.log(symmetricKey);
    const decryptedIv = new Uint8Array(base64ToArrayBuffer(iv));
    console.log(decryptedIv);
    const fileResponse = await fetch(`/downloadEncryptedFile?id=${id}`);
    if (!fileResponse.ok) {
      throw new Error('Failed to download file');
    }
    const responseData = await fileResponse.json();
    console.log(responseData);
    const encryptedFileContent = new Uint8Array(base64ToArrayBuffer(responseData.fileContent));
    console.log(encryptedFileContent);
    const decryptedContent = await decryptFile(encryptedFileContent, symmetricKey, decryptedIv);
    const decryptedBlob = new Blob([decryptedContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(decryptedBlob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = fileName;
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