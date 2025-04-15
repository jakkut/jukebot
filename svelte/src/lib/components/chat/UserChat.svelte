<script>
	let { children, class: className = "" } = $props();
</script>

<p class="bg-white w-fit text-black px-3 py-2 rounded-lg {className}">
	{@render children()}
</p>
