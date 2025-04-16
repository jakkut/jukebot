<script>
	// mode controls whether the form is used for "login" or "register"
	let mode = "login";
	let username = "";
	let password = "";
	let errorMsg = "";

	// Handle form submission for login or create account.
	async function handleSubmit(event) {
		event.preventDefault();
		// Choose the endpoint based on current mode.
		const endpoint =
			mode === "login"
				? "http://localhost:8000/login"
				: "http://localhost:8000/create_account";

		// Build form data from the current form.
		const formData = new FormData(event.currentTarget);

		try {
			const res = await fetch(endpoint, {
				method: "POST",
				body: formData,
				headers: { Accept: "application/json" },
				credentials: "include",
			});

			const data = await res.json();
			if (data.redirect) {
				window.location.href = data.redirect;
			} else if (data.error) {
				console.error(data.error);
			}
		} catch (err) {
			console.error("Submission error:", err);
		}
	}

	// Handle the Guest Login option.
	async function handleGuestLogin() {
		try {
			const res = await fetch("http://localhost:8000/guest-login", {
				method: "GET",
				headers: { Accept: "application/json" },
				credentials: "include",
			});
			// If the response is redirected, override and send the user to Svelte's route.
			if (res.redirected) {
				window.location.href = res.url;
				return;
			}

			const data = await res.json();
			if (data.redirect) {
				window.location.href = data.redirect;
			} else if (data.error) {
				console.error(data.error);
			}
		} catch (err) {
			console.error("Submission error:", err);
		}
	}

	// Function to switch the mode and clear errors.
	function switchMode(newMode) {
		mode = newMode;
		errorMsg = "";
		username = "";
		password = "";
	}
</script>

<!-- Outer Container -->
<div class="flex items-center justify-center min-h-screen bg-gray-900">
	<div class="w-full max-w-md p-8 bg-gray-800 border border-gray-700 shadow-2xl rounded-lg">
		<!-- Toggle Buttons -->
		<div class="flex justify-around mb-6">
			<button
				onclick={() => switchMode("login")}
				aria-label="Switch to login mode"
				class="px-4 py-2 rounded transition-colors duration-200 focus:outline-none {mode ===
				'login'
					? 'bg-slate-700 text-white'
					: 'bg-gray-700 text-gray-400'}"
			>
				Login
			</button>
			<button
				onclick={() => switchMode("register")}
				aria-label="Switch to create account mode"
				class="px-4 py-2 rounded transition-colors duration-200 focus:outline-none {mode ===
				'register'
					? 'bg-slate-700 text-white'
					: 'bg-gray-700 text-gray-400'}"
			>
				Create Account
			</button>
		</div>

		<!-- Single Unified Form for Login / Registration -->
		<form
			onsubmit={handleSubmit}
			method="post"
			action={mode === "login"
				? "http://localhost:8000/login"
				: "http://localhost:8000/create_account"}
		>
			<div class="mb-4">
				<label for="username" class="block text-gray-300 font-medium mb-1"
					>Username</label
				>
				<input
					id="username"
					name="username"
					type="text"
					bind:value={username}
					required
					class="w-full p-3 bg-gray-700 border border-gray-600 text-white rounded focus:outline-none focus:ring-2 focus:ring-slate-500"
				/>
			</div>
			<div class="mb-6">
				<label for="password" class="block text-gray-300 font-medium mb-1"
					>Password</label
				>
				<input
					id="password"
					name="password"
					type="password"
					bind:value={password}
					required
					class="w-full p-3 bg-gray-700 border border-gray-600 text-white rounded focus:outline-none focus:ring-2 focus:ring-slate-500"
				/>
			</div>
			<button
				type="submit"
				class="w-full bg-slate-700 text-white py-3 px-4 rounded hover:bg-slate-600 transition-colors"
			>
				{mode === "login" ? "Login" : "Create Account"}
			</button>
		</form>

		{#if errorMsg}
			<p class="mt-4 text-red-500 text-center">{errorMsg}</p>
		{/if}

		<!-- Guest Login Option -->
		<div class="mt-6 text-center">
			<p class="text-sm text-gray-400">
				Or continue as a
				<button class="text-slate-400 hover:underline" onclick={handleGuestLogin}
					>Guest</button
				>
			</p>
		</div>
	</div>
</div>
