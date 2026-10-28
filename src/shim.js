// Gives the app the same small interface it used inside claude.ai
// (claude.use('db' | 'user' | 'downloads')), backed by Firebase.
import { initializeApp } from 'firebase/app';
import {
  getAuth, GoogleAuthProvider, signInWithPopup, signInWithRedirect,
  getRedirectResult, onAuthStateChanged, signOut
} from 'firebase/auth';
import {
  initializeFirestore, persistentLocalCache, persistentMultipleTabManager,
  doc, getDoc, setDoc, onSnapshot
} from 'firebase/firestore';

const firebaseConfig = {
  apiKey: 'AIzaSyDxbiom1f6pa2o4vlOxPBAMDx3ZjZ5Fq8M',
  authDomain: 'workbench-5cc25.firebaseapp.com',
  projectId: 'workbench-5cc25',
  storageBucket: 'workbench-5cc25.firebasestorage.app',
  messagingSenderId: '877255474382',
  appId: '1:877255474382:web:8762e208183478f35c249f'
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
let db;
try {
  db = initializeFirestore(app, {
    localCache: persistentLocalCache({ tabManager: persistentMultipleTabManager() })
  });
} catch (e) {
  db = initializeFirestore(app, {});
}

let first = true;
const authReady = new Promise(res => {
  onAuthStateChanged(auth, user => {
    if (first) { first = false; res(user); return; }
    window.dispatchEvent(new CustomEvent('wb-auth', { detail: { signedIn: !!user } }));
  });
});
getRedirectResult(auth).catch(() => {});

function fixErr(e) {
  const x = new Error((e && e.message) || 'error');
  x.code = String((e && e.code) || '').replace(/^firestore\//, '').replace(/-/g, '_');
  return x;
}

function refFor(path) { return doc(db, ...path.split('/')); }
const wrapSnap = s => ({ exists: s.exists(), data: () => s.data(), metadata: s.metadata });

const dbApi = {
  doc(path) {
    const ref = refFor(path);
    return {
      async get() { try { return wrapSnap(await getDoc(ref)); } catch (e) { throw fixErr(e); } },
      async set(obj) { try { await setDoc(ref, obj); } catch (e) { throw fixErr(e); } },
      onSnapshot(cb, errCb) {
        return onSnapshot(ref, s => cb(wrapSnap(s)), e => { if (errCb) errCb(fixErr(e)); });
      }
    };
  }
};

const userApi = { async id() { await authReady; return auth.currentUser ? auth.currentUser.uid : null; } };

const downloadsApi = {
  async save({ filename, data }) {
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  }
};

window.claude = {
  async use(name) {
    if (name === 'db') return dbApi;
    if (name === 'user') return userApi;
    if (name === 'downloads') return downloadsApi;
    return null;
  }
};

window.WBAuth = {
  ready: authReady,
  email() { return auth.currentUser ? auth.currentUser.email : null; },
  async signIn() {
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
      return { ok: true };
    } catch (e) {
      const c = e && e.code;
      if (c === 'auth/popup-blocked' || c === 'auth/operation-not-supported-in-this-environment') {
        try { await signInWithRedirect(auth, provider); return { ok: true }; } catch (e2) { return { ok: false, code: e2 && e2.code }; }
      }
      if (c === 'auth/popup-closed-by-user' || c === 'auth/cancelled-popup-request') return { ok: false, cancelled: true };
      return { ok: false, code: c };
    }
  },
  async signOut() { await signOut(auth); }
};
