<script>
	let { children, class: className = "" } = $props();
</script>

<div class="text-left {className}">{@render children()}</div>
