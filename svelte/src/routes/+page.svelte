<script lang="js">
	import { AssistantChat, UserChat, PlaylistPreview } from "$lib";
	import { onMount } from "svelte";
	import { slide } from "svelte/transition";

	let user_id = $state("");
	let conversations = $state([]);
	let selectedChat = $state([]);
	let inputText = $state("");

	// Collapsible sidebar state
	let sidebarOpen = $state(true);

	function toggleSidebar() {
		sidebarOpen = !sidebarOpen;
	}

	onMount(async () => {
		const res = await fetch("http://localhost:8000/get_history", {
			method: "GET",
			headers: { Accept: "application/json" },
			credentials: "include", // Ensure cookies are included
		});

		const data = await res.json();
		user_id = data.user_id;
		conversations = data.conversations;
		selectedChat = conversations[0];
	});

	async function handleLogout() {
		try {
			const response = await fetch("http://localhost:8000/logout", {
				method: "GET",
				headers: { Accept: "application/json" },
				credentials: "include",
			});
			const data = await response.json();
			if (data.redirect) {
				window.location.href = data.redirect;
			}
		} catch (error) {
			console.error("Logout error:", error);
		}
	}

	async function handleSubmit(e) {
		e.preventDefault();
		const formData = new FormData(e.target);
		const content = formData.get("content");

		try {
			const res = await fetch("http://localhost:8000/generate_songs", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ user_id, content }),
				credentials: "include",
			});
			const data = await res.json();
			inputText = ""; // Clears input field
			console.log(data);
		} catch (error) {
			console.error(error);
		}
	}
</script>

{#if conversations.length !== 0}
	<!-- Outer container: full height, dark background, flex layout -->
	<div class="min-h-screen bg-gray-900 flex">
		<!-- Sidebar -->
		<div
			class={`relative flex flex-col transition-all duration-300 bg-accent-grey text-white rounded-md shadow-lg ${
				sidebarOpen ? "w-72" : "w-16"
			}`}
		>
			<!-- Toggle button (always visible) -->
			<button
				on:click={toggleSidebar}
				class="absolute -right-3 top-4 bg-white text-black rounded-full px-2 py-1 shadow-md"
			>
				{#if sidebarOpen}
					&lt;
				{:else}
					&gt;
				{/if}
			</button>

			{#if sidebarOpen}
				<!-- Expanded Sidebar -->
				<div class="p-4 mb-2">
					<h1 class="block font-sans text-xl font-semibold">Jukebot</h1>
				</div>
				<nav
					class="flex min-w-[240px] flex-col gap-1 p-2 font-sans text-base font-normal text-blue-gray-700"
				>
					<div class="relative block w-full">
						{#each conversations as chat, i}
							<div class={chat.name == selectedChat.name ? "bg-back-grey" : ""}>
								<button
									class="w-full text-left px-4 py-2 hover:bg-white/20 transition-colors rounded"
									on:click={() => {
										selectedChat = conversations[i];
									}}
								>
									{chat.name}
								</button>
							</div>
						{/each}
					</div>
					<hr class="my-2 border-blue-gray-50" />
					<div
						role="button"
						class="flex items-center w-full p-3 leading-tight transition-all rounded-lg outline-none text-start hover:bg-blue-gray-50 hover:bg-opacity-80 hover:text-blue-gray-900 focus:bg-blue-gray-50 focus:bg-opacity-80 focus:text-blue-gray-900 active:bg-blue-gray-50 active:bg-opacity-80 active:text-blue-gray-900"
					>
						<div class="grid mr-4 place-items-center">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								aria-hidden="true"
								class="w-5 h-5"
							>
								<path
									fill-rule="evenodd"
									d="M18.685 19.097A9.723 9.723 0 0021.75 12c0-5.385-4.365-9.75-9.75-9.75S2.25 6.615 2.25 12a9.723 9.723 0 003.065 7.097A9.716 9.716 0 0012 21.75a9.716 9.716 0 006.685-2.653zm-12.54-1.285A7.486 7.486 0 0112 15a7.486 7.486 0 015.855 2.812A8.224 8.224 0 0112 20.25a8.224 8.224 0 01-5.855-2.438zM15.75 9a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z"
									clip-rule="evenodd"
								></path>
							</svg>
						</div>
						Profile
					</div>
					<div
						role="button"
						class="flex items-center w-full p-3 leading-tightrounded-lg text-start transition-transform hover:scale-105 duration-200"
					>
						<div class="grid mr-4 place-items-center">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								aria-hidden="true"
								class="w-5 h-5"
							>
								<path
									fill-rule="evenodd"
									d="M11.078 2.25c-.917 0-1.699.663-1.85 1.567L9.05 4.889c-.02.12-.115.26-.297.348a7.493 7.493 0 00-.986.57c-.166.115-.334.126-.45.083L6.3 5.508a1.875 1.875 0 00-2.282.819l-.922 1.597a1.875 1.875 0 00.432 2.385l.84.692c.095.078.17.229.154.43a7.598 7.598 0 000 1.139c.015.2-.059.352-.153.43l-.841.692a1.875 1.875 0 00-.432 2.385l.922 1.597a1.875 1.875 0 002.282.818l1.019-.382c.115-.043.283-.031.45.082.312.214.641.405.985.57.182.088.277.228.297.35l.178 1.071c.151.904.933 1.567 1.85 1.567h1.844c.916 0 1.699-.663 1.85-1.567l.178-1.072c.02-.12.114-.26.297-.349.344-.165.673-.356.985-.57.167-.114.335-.125.45-.082l1.02.382a1.875 1.875 0 002.28-.819l.923-1.597a1.875 1.875 0 00-.432-2.385l-.84-.692c-.095-.078-.17-.229-.154-.43a7.614 7.614 0 000-1.139c-.016-.2.059-.352.153-.43l.84-.692c.708-.582.891-1.59.433-2.385l-.922-1.597a1.875 1.875 0 00-2.282-.818l-1.02.382c-.114.043-.282.031-.449-.083a7.49 7.49 0 00-.985-.57c-.183-.087-.277-.227-.297-.348l-.179-1.072a1.875 1.875 0 00-1.85-1.567h-1.843zM12 15.75a3.75 3.75 0 100-7.5 3.75 3.75 0 000 7.5z"
									clip-rule="evenodd"
								></path>
							</svg>
						</div>
						Settings
					</div>
					<button
						class="flex items-center w-full p-3 leading-tightrounded-lg text-start transition-transform hover:scale-105 duration-200"
						on:click={handleLogout}
					>
						<div class="grid mr-4 place-items-center">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								aria-hidden="true"
								class="w-5 h-5"
							>
								<path
									fill-rule="evenodd"
									d="M12 2.25a.75.75 0 01.75.75v9a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM6.166 5.106a.75.75 0 010 1.06 8.25 8.25 0 1011.668 0 .75.75 0 111.06-1.06c3.808 3.807 3.808 9.98 0 13.788-3.807 3.807-9.98 3.807-13.788 0-3.808-3.807-3.808-9.98 0-13.788a.75.75 0 011.06 0z"
									clip-rule="evenodd"
								></path>
							</svg>
						</div>
						Log Out
					</button>
				</nav>
			{:else}
				<!-- Collapsed Sidebar (minimal icons only) -->
				<nav class="flex flex-col gap-4 p-2 mt-4 items-center">
					<button
						title="Profile"
						class="p-2 transition-transform hover:scale-105 duration-200 rounded-md"
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 24 24"
							fill="currentColor"
							class="w-5 h-5"
						>
							<path
								fill-rule="evenodd"
								d="M18.685 19.097A9.723 9.723 0 0021.75 12c0-5.385-4.365-9.75-9.75-9.75S2.25 6.615 2.25 12a9.723 9.723 0 003.065 7.097A9.716 9.716 0 0012 21.75a9.716 9.716 0 006.685-2.653zm-12.54-1.285A7.486 7.486 0 0112 15a7.486 7.486 0 015.855 2.812A8.224 8.224 0 0112 20.25a8.224 8.224 0 01-5.855-2.438zM15.75 9a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z"
								clip-rule="evenodd"
							></path>
						</svg>
					</button>
					<button
						title="Settings"
						class="p-2 transition-transform hover:scale-105 duration-200 rounded-md"
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 24 24"
							fill="currentColor"
							class="w-5 h-5"
						>
							<path
								fill-rule="evenodd"
								d="M11.078 2.25c-.917 0-1.699.663-1.85 1.567L9.05 4.889c-.02.12-.115.26-.297.348a7.493 7.493 0 00-.986.57c-.166.115-.334.126-.45.083L6.3 5.508a1.875 1.875 0 00-2.282.819l-.922 1.597a1.875 1.875 0 00.432 2.385l.84.692c.095.078.17.229.154.43a7.598 7.598 0 000 1.139c.015.2-.059.352-.153.43l-.841.692a1.875 1.875 0 00-.432 2.385l.922 1.597a1.875 1.875 0 002.282.818l1.019-.382c.115-.043.283-.031.45.082.312.214.641.405.985.57.182.088.277.228.297.35l.178 1.071c.151.904.933 1.567 1.85 1.567h1.844c.916 0 1.699-.663 1.85-1.567l.178-1.072c.02-.12.114-.26.297-.349.344-.165.673-.356.985-.57.167-.114.335-.125.45-.082l1.02.382a1.875 1.875 0 002.28-.819l.923-1.597a1.875 1.875 0 00-.432-2.385l-.84-.692c-.095-.078-.17-.229-.154-.43a7.614 7.614 0 000-1.139c-.016-.2.059-.352.153-.43l.84-.692c.708-.582.891-1.59.433-2.385l-.922-1.597a1.875 1.875 0 00-2.282-.818l-1.02.382c-.114.043-.282.031-.449-.083a7.49 7.49 0 00-.985-.57c-.183-.087-.277-.227-.297-.348l-.179-1.072a1.875 1.875 0 00-1.85-1.567h-1.843zM12 15.75a3.75 3.75 0 100-7.5 3.75 3.75 0 000 7.5z"
								clip-rule="evenodd"
							></path>
						</svg>
					</button>
					<button
						title="Log Out"
						class="p-2 transition-transform hover:scale-105 duration-200 rounded-md"
						on:click={handleLogout}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 24 24"
							fill="currentColor"
							class="w-5 h-5"
						>
							<path
								fill-rule="evenodd"
								d="M12 2.25a.75.75 0 01.75.75v9a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM6.166 5.106a.75.75 0 010 1.06 8.25 8.25 0 1011.668 0 .75.75 0 111.06-1.06c3.808 3.807 3.808 9.98 0 13.788-3.807 3.807-9.98 3.807-13.788 0-3.808-3.807-3.808-9.98 0-13.788a.75.75 0 011.06 0z"
								clip-rule="evenodd"
							></path>
						</svg>
					</button>
				</nav>
			{/if}
		</div>

		<!-- Main Chat Section -->
		<div class="relative text-white w-full min-h-screen flex flex-col overflow-hidden">
			<!-- Conversation Title with black-to-green gradient -->
			<div class="w-full px-8 mt-4">
				<h2 class="text-2xl font-bold py-2 rounded">
					{selectedChat.name}
				</h2>
				<hr class="my-4 w-full border-gray-500" />
			</div>

			<!-- Chat History -->
			<div class="flex flex-col px-8 h-[80vh] overflow-y-scroll overflow-x-hidden">
				{#each selectedChat.history as chat}
					<div class="my-3">
						{#if chat.role == "user"}
							<UserChat class="float-right">{chat.message}</UserChat>
						{:else if typeof chat.message === "object" && !Array.isArray(chat.message) && chat.message !== null}
							<PlaylistPreview data={chat.message} />
						{:else}
							<AssistantChat>{chat.message}</AssistantChat>
						{/if}
					</div>
				{/each}
			</div>

			<!-- Input Form -->
			<footer class="px-8 py-4 bg-gray-800">
				<form on:submit={handleSubmit} class="flex items-center">
					<input
						type="text"
						name="content"
						placeholder="Type your desired playlist vibe..."
						class="flex-1 p-2 bg-gray-700 border border-gray-600 text-white rounded-md placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-400"
						bind:value={inputText}
					/>
					<button
						type="submit"
						class="ml-4 p-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-500 transition-colors"
					>
						Submit
					</button>
				</form>
			</footer>
		</div>
	</div>
{/if}
