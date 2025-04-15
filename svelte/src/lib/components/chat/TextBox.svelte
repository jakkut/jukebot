<script>
	let { class: className } = $props();
</script>

<div class="w-full bg-juke-green p-4 {className}">
	<input
		type="text"
		id="mainTextBox"
		placeholder="Type your desired playlist vibe..."
		class="p-2 w-[90%] border"
	/>
	<button id="submitBtn" class="p-2 bg-juke-red float-right w-[9%]">Submit</button>
</div>
