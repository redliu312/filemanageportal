# Frontend File Upload Implementation - Detailed Line-by-Line

## 1. UI Component ([`frontend/src/app/files/page.tsx`](frontend/src/app/files/page.tsx))

### State Management (Lines 14-22)
```typescript
14 |   const [uploading, setUploading] = useState(false);
21 |   const [uploadProgress, setUploadProgress] = useState<number>(0);
22 |   const fileInputRef = useRef<HTMLInputElement>(null);
```
- **Line 14**: `uploading` - Boolean flag to disable UI during upload
- **Line 21**: `uploadProgress` - Number (0-100) for progress bar
- **Line 22**: `fileInputRef` - Reference to file input element for resetting

### Upload Handler (Lines 50-75)
```typescript
50 |   const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
51 |     const file = e.target.files?.[0];
52 |     if (!file) return;
53 | 
54 |     try {
55 |       setUploading(true);
56 |       setError('');
57 |       setSuccess('');
58 |       setUploadProgress(0);
59 |       
60 |       await api.uploadFile(file, (progress) => {
61 |         setUploadProgress(Math.round(progress));
62 |       });
63 |       
64 |       setSuccess('File uploaded successfully!');
65 |       loadFiles();
66 |       if (fileInputRef.current) {
67 |         fileInputRef.current.value = '';
68 |       }
69 |     } catch (err) {
70 |       setError(err instanceof Error ? err.message : 'Failed to upload file');
71 |     } finally {
72 |       setUploading(false);
73 |       setUploadProgress(0);
74 |     }
75 |   };
```
- **Line 51**: Extract first file from input
- **Line 55**: Set uploading flag to true (disables upload button)
- **Line 58**: Reset progress to 0
- **Line 60-62**: Call API with progress callback that updates state
- **Line 65**: Refresh file list after successful upload
- **Line 67**: Clear file input for next upload
- **Line 72-73**: Reset uploading state and progress

### File Input HTML (Lines 159-166)
```typescript
159 |           <input
160 |             ref={fileInputRef}
161 |             type="file"
162 |             onChange={handleFileUpload}
163 |             disabled={uploading}
164 |             className="hidden"
165 |             id="file-upload"
166 |           />
```
- **Line 160**: Attach ref for programmatic reset
- **Line 162**: Trigger `handleFileUpload` when file selected
- **Line 163**: Disable during upload
- **Line 164**: Hidden (styled with label)

### Upload Button (Lines 167-189)
```typescript
167 |           <label
168 |             htmlFor="file-upload"
169 |             className={`cursor-pointer ... ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
170 |           >
171 |             {uploading ? (
172 |               <>
173 |                 <svg className="animate-spin ...">...</svg>
174 |                 Uploading...
175 |               </>
176 |             ) : (
177 |               <>
178 |                 <svg className="w-5 h-5 mr-2">...</svg>
179 |                 Upload File
180 |               </>
181 |             )}
182 |           </label>
```
- **Line 169**: Disable cursor when uploading
- **Line 171-175**: Show spinner during upload
- **Line 177-180**: Show upload icon when idle

### Progress Bar (Lines 194-205)
```typescript
194 |           {uploading && (
195 |             <div className="mt-4">
196 |               <div className="bg-gray-200 rounded-full h-2.5">
197 |                 <div
198 |                   className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
199 |                   style={{ width: `${uploadProgress}%` }}
200 |                 ></div>
201 |               </div>
202 |               <p className="mt-2 text-sm text-gray-600">{uploadProgress}% uploaded</p>
203 |             </div>
204 |           )}
```
- **Line 194**: Only show when uploading
- **Line 199**: Dynamic width based on progress (0-100%)
- **Line 202**: Display percentage text

## 2. API Client ([`frontend/src/lib/api.ts`](frontend/src/lib/api.ts))

### Upload Method (Lines 124-176)
```typescript
124 |   async uploadFile(
125 |     file: File,
126 |     onProgress?: (progress: number) => void
127 |   ): Promise<FileUploadResponse> {
128 |     const formData = new FormData();
129 |     formData.append('file', file);
130 | 
131 |     const url = `${this.baseUrl}/api/files`;
132 |     const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
133 | 
134 |     return new Promise((resolve, reject) => {
135 |       const xhr = new XMLHttpRequest();
136 | 
137 |       // Track upload progress
138 |       if (onProgress) {
139 |         xhr.upload.addEventListener('progress', (event) => {
140 |           if (event.lengthComputable) {
141 |             const percentComplete = (event.loaded / event.total) * 100;
142 |             onProgress(percentComplete);
143 |           }
144 |         });
145 |       }
146 | 
147 |       xhr.addEventListener('load', () => {
148 |         try {
149 |           const data = JSON.parse(xhr.responseText);
150 |           if (xhr.status >= 200 && xhr.status < 300) {
151 |             resolve(data);
152 |           } else {
153 |             reject(new Error(data.error || 'Failed to upload file'));
154 |           }
155 |         } catch (error) {
156 |           reject(new Error('Failed to parse response'));
157 |         }
158 |       });
159 | 
160 |       xhr.addEventListener('error', () => {
161 |         reject(new Error('Network error occurred'));
162 |       });
163 | 
164 |       xhr.addEventListener('abort', () => {
165 |         reject(new Error('Upload cancelled'));
166 |       });
167 | 
168 |       xhr.open('POST', url);
169 |       
170 |       if (token) {
171 |         xhr.setRequestHeader('Authorization', `Bearer ${token}`);
172 |       }
173 | 
174 |       xhr.send(formData);
175 |     });
176 |   }
```
- **Line 128-129**: Create FormData and append file
- **Line 132**: Get JWT token from localStorage
- **Line 135**: Use XMLHttpRequest (not fetch) for progress tracking
- **Line 139-144**: Listen to upload progress events
- **Line 141**: Calculate percentage: (loaded / total) × 100
- **Line 142**: Call callback with progress percentage
- **Line 147-158**: Handle successful response
- **Line 160-166**: Handle errors and cancellation
- **Line 168**: Open POST request
- **Line 171**: Add JWT token to headers
- **Line 174**: Send FormData

## Key Frontend Flow

```
User clicks upload button (Line 167)
  ↓
File input triggers onChange (Line 162)
  ↓
handleFileUpload called (Line 50)
  ↓
Set uploading=true, progress=0 (Lines 55, 58)
  ↓
Call api.uploadFile with callback (Line 60)
  ↓
XMLHttpRequest sends file (Line 174)
  ↓
Progress events update state (Lines 139-142 → 61)
  ↓
Progress bar updates (Line 199)
  ↓
Upload completes (Line 147)
  ↓
Refresh file list (Line 65)
  ↓
Reset state (Lines 72-73)
```

**Why XMLHttpRequest instead of fetch?**
- `fetch` API doesn't support upload progress tracking
- `XMLHttpRequest.upload.progress` event provides real-time progress
- This is the only way to show upload percentage in browsers