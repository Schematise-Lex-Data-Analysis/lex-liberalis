<script lang="ts">
  import { writable } from "svelte/store";
  
  type Folder = {
    id: string;
    name: string;
    files: File[];
    expanded: boolean;
  };
  
  type File = {
    id: string;
    name: string;
    content: File | string | null; // content can be file object or text content for .txt files
    url: string;
    type: "pdf" | "txt"; // added type to distinguish between file types
  };
  
  let folders: Folder[] = [];
  let pdfUrl: string | null = null;
  let textContent: string | null = null; // To hold content for text files
  let showModal = false;
  let searchQuery = ""; // To store the search query
  let searchResults: { file: File; folderName: string }[] = []; // To store search results
  
  const generateId = () => Math.random().toString(36).substring(2, 10);
  
  function createFolder() {
    folders = [
      ...folders,
      { id: generateId(), name: "New Folder", files: [], expanded: true },
    ];
  }
  
  function renameFolder(folderId: string, newName: string) {
    folders = folders.map((folder) =>
      folder.id === folderId ? { ...folder, name: newName } : folder
    );
  }
  
  function deleteFolder(folderId: string) {
    folders = folders.filter((folder) => folder.id !== folderId);
  }
  
  async function uploadFileToFolder(folderId: string, event: Event) {
  const input = event.target as HTMLInputElement;
  if (!input.files || input.files.length === 0) return;

  const file = input.files[0];
  const fileType = file.type;

  // Check file type
  if (fileType !== "application/pdf" && fileType !== "text/plain") {
    alert("Only PDF and Text files are allowed.");
    return;
  }

  const url = URL.createObjectURL(file); // Create a temporary URL for viewing
  const formData = new FormData();
  formData.append("folderName", folders.find(folder => folder.id === folderId)?.name || "Unknown Folder");
  formData.append("file", file);

  // Send file to the backend
  try {
    const response = await fetch("http://127.0.0.1:5000/api/savefile/preview", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to upload file to the server");
    }

    const textFileContent = fileType === "text/plain" ? await readFileContent(file) : null;

    folders = folders.map((folder) =>
      folder.id === folderId
        ? {
            ...folder,
            files: [
              ...folder.files,
              {
                id: generateId(),
                name: file.name,
                content: fileType === "application/pdf" ? file : textFileContent,
                url,
                type: fileType === "application/pdf" ? "pdf" : "txt",
              },
            ],
          }
        : folder
    );
  } catch (error) {
    console.error("Error uploading file:", error);
    alert("Failed to upload file to the server. Please try again.");
  }
}

  
  function readFileContent(file: File): string {
    const reader = new FileReader();
    reader.readAsText(file);
    return new Promise<string>((resolve) => {
      reader.onload = () => resolve(reader.result as string);
    });
  }
  
  async function deleteFile(folderId: string, fileId: string) {
  // Find the folder and the file within it
  const folder = folders.find((folder) => folder.id === folderId);
  const file = folder?.files.find((file) => file.id === fileId);

  if (!folder || !file) {
    alert("Folder or file not found.");
    return;
  }

  // Send DELETE request to the backend
  try {
    const response = await fetch("http://127.0.0.1:5000/api/deletefile", {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        folderName: folder.name,
        fileName: file.name,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to delete file from the server");
    }

    // Update the folders array after successful deletion
    folders = folders.map((folder) =>
      folder.id === folderId
        ? {
            ...folder,
            files: folder.files.filter((file) => file.id !== fileId), // Remove the file from the files array
          }
        : folder
    );

    alert("File deleted successfully!");
  } catch (error) {
    console.error("Error deleting file:", error);
    alert("Failed to delete file from the server. Please try again.");
  }
}

  
  function toggleFolder(folderId: string) {
    folders = folders.map((folder) =>
      folder.id === folderId ? { ...folder, expanded: !folder.expanded } : folder
    );
  }
  
  function openPdf(url: string) {
    pdfUrl = url;
    showModal = true;
  }
  
  function closeModal() {
    showModal = false;
    pdfUrl = null;
    textContent = null; // Reset text content when closing modal
  }
  
  // Search function
  function searchFiles() {
    const query = searchQuery.trim().toLowerCase();
    if (!query) {
      searchResults = [];
      return;
    }
  
    searchResults = [];
    folders.forEach((folder) => {
      folder.files.forEach((file) => {
        if (file.name.toLowerCase().includes(query)) {
          searchResults.push({ file, folderName: folder.name });
        }
      });
    });
  }
</script>

<div class="explorer bg-white text-gray-900 text-sm font-mono p-4 shadow-md h-full w-full mt-4">
  <!-- Explorer Header -->
  <div class="explorer-header flex justify-between items-center mb-4">
    <span class="text-xs uppercase text-gray-500">Explorer</span>
    <button
      on:click={createFolder}
      class="text-gray-500 hover:text-black"
      title="New Folder"
    >
      ➕
    </button>
  </div>
  
  <!-- Search Bar -->
  <div class="search-bar mb-4">
    <input
      type="text"
      placeholder="Search files..."
      bind:value={searchQuery}
      on:input={searchFiles}
      class="w-full p-2 border border-gray-300 rounded text-gray-900"
    />
  </div>
  
  <!-- Search Results -->
  {#if searchQuery.trim() && searchResults.length > 0}
    <div class="search-results mb-4">
      <h3 class="text-gray-500 text-xs uppercase">Search Results</h3>
      <ul>
        {#each searchResults as { file, folderName }}
          <li
            class="flex justify-between items-center py-2 border-b text-sm cursor-pointer hover:bg-gray-100"
            on:click={() => openPdf(file.url)}
          >
            <span>{file.name}</span>
            <span class="text-gray-400 text-xs">{folderName}</span>
          </li>
        {/each}
      </ul>
    </div>
  {/if}
  
  <!-- Tree View -->
  <ul class="folder-tree space-y-1">
    {#each folders as folder (folder.id)}
      <li class="folder-item">
        <!-- Folder Header -->
        <div class="folder-header flex items-center group">
          <button
            on:click={() => toggleFolder(folder.id)}
            class="toggle-icon text-gray-500 hover:text-black mr-1"
          >
            {folder.expanded ? "▼" : "▶"}
          </button>
          <input
            type="text"
            bind:value={folder.name}
            class="folder-name bg-transparent border-none outline-none flex-grow text-gray-900"
            on:change={(e) => renameFolder(folder.id, e.target.value)}
          />
          <div class="folder-actions opacity-100 flex space-x-1">
            <label
              title="Upload File"
              class="text-gray-500 hover:text-black cursor-pointer"
            >
              📂
              <input
                type="file"
                accept=".pdf, .txt"
                class="hidden"
                on:change={(e) => uploadFileToFolder(folder.id, e)}
              />
            </label>
            <button
              on:click={() => deleteFolder(folder.id)}
              class="text-red-500 hover:text-red-700"
              title="Delete Folder"
            >
              ❌
            </button>
          </div>
        </div>
  
        <!-- Folder Contents -->
        {#if folder.expanded}
          <ul class="file-list pl-4 space-y-1 py-1">
            {#each folder.files as file (file.id)}
              <li class="file-item flex justify-between items-center group">
                <span
                  class="cursor-pointer text-blue-500 hover:underline"
                  on:click={() => openPdf(file.url)}
                >
                  {file.name}
                </span>
                <button
                  on:click={() => deleteFile(folder.id, file.id)}
                  class="text-red-500 hover:text-red-700 opacity-100"
                  title="Delete File"
                >
                  ❌
                </button>
              </li>
            {/each}
          </ul>
        {/if}
      </li>
    {/each}
  </ul>
</div>

<!-- Modal for PDF Viewer or Text Viewer -->
{#if showModal}
  <div class="fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center w-full z-50 justify-center">
    <div class="bg-white p-4 rounded shadow-lg max-w-3xl w-full">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-bold">Viewer</h2>
        <button
          on:click={closeModal}
          class="text-gray-500 hover:text-black"
        >
          ❌
        </button>
      </div>
      {#if pdfUrl}
        <iframe
          src={pdfUrl}
          class="w-full h-96 border rounded"
          frameborder="0"
        ></iframe>
      {:else if textContent}
        <pre class="w-full h-96 overflow-auto">{textContent}</pre>
      {/if}
    </div>
  </div>
{/if}