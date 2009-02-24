_LzmaDecodeProperties:
	pushl	%ebp
	movl	$1, %edx
	movl	%esp, %ebp
	cmpl	$4, 16(%ebp)
	movl	8(%ebp), %ecx
	jle	L1
	movl	12(%ebp), %eax
	movzbl	(%eax), %eax
	cmpb	$-32, %al
	ja	L1
	movl	$0, 8(%ecx)
	cmpb	$44, %al
	jbe	L13
	xorb	%dl, %dl
L7:
	subb	$45, %al
	incl	%edx
	cmpb	$44, %al
	ja	L7
	movl	%edx, 8(%ecx)
L13:
	movl	$0, 4(%ecx)
	cmpb	$8, %al
	jbe	L15
	xorl	%edx, %edx
L11:
	subb	$9, %al
	incl	%edx
	cmpb	$8, %al
	ja	L11
	movl	%edx, 4(%ecx)
L15:
	movzbl	%al, %eax
	xorl	%edx, %edx
	movl	%eax, (%ecx)
L1:
	popl	%ebp
	movl	%edx, %eax
	ret

_LzmaDecode:
	pushl	%ebp
	movl	%esp, %ebp
	pushl	%edi
	pushl	%esi
	pushl	%ebx
	subl	$152, %esp
	movl	8(%ebp), %edx
	movl	$0, -20(%ebp)
	movb	$0, -21(%ebp)
	movl	12(%edx), %eax
	movl	$0, -40(%ebp)
	movl	8(%edx), %ecx
	movl	$1, -44(%ebp)
	movl	(%edx), %esi
	movl	%eax, -16(%ebp)
	movl	$1, %eax
	movl	%eax, %ebx
	movl	%esi, -36(%ebp)
	sall	%cl, %ebx
	movl	%ebx, %ecx
	movl	$1, -48(%ebp)
	decl	%ecx
	movl	%ecx, -28(%ebp)
	movl	4(%edx), %ecx
	movl	$1, -52(%ebp)
	movl	$1, -56(%ebp)
	sall	%cl, %eax
	decl	%eax
	movl	%eax, -32(%ebp)
	movl	32(%ebp), %ecx
	movl	20(%ebp), %eax
	movl	$0, (%eax)
	movl	$768, %eax
	movl	$0, (%ecx)
	movl	%esi, %ecx
	addl	4(%edx), %ecx
	xorl	%edx, %edx
	sall	%cl, %eax
	addl	$1846, %eax
L158:
	cmpl	%eax, %edx
	jae	L132
	movl	-16(%ebp), %ebx
	movw	$1024, (%ebx,%edx,2)
	incl	%edx
	jmp	L158
L132:
	movl	$-1, -68(%ebp)
	movl	12(%ebp), %ebx
	xorl	%edi, %edi
	xorl	%edx, %edx
	movl	%ebx, %esi
	addl	16(%ebp), %esi
	movl	%esi, -64(%ebp)
L27:
	cmpl	-64(%ebp), %ebx
	je	L155
	movzbl	(%ebx), %eax
	sall	$8, %edi
	incl	%edx
	incl	%ebx
	orl	%eax, %edi
	cmpl	$4, %edx
	jle	L27
	movl	28(%ebp), %eax
	cmpl	%eax, -20(%ebp)
	jae	L129
L128:
	movl	-20(%ebp), %edx
	movl	-40(%ebp), %eax
	movl	-16(%ebp), %ecx
	andl	-28(%ebp), %edx
	sall	$4, %eax
	addl	%edx, %eax
	cmpl	$16777215, -68(%ebp)
	leal	(%ecx,%eax,2), %eax
	movl	%edx, -76(%ebp)
	movl	%eax, -72(%ebp)
	ja	L30
	cmpl	-64(%ebp), %ebx
	je	L155
	sall	$8, -68(%ebp)
	sall	$8, %edi
	movzbl	(%ebx), %eax
	incl	%ebx
	orl	%eax, %edi
L30:
	movl	-72(%ebp), %eax
	movl	-68(%ebp), %ecx
	movzwl	(%eax), %esi
	shrl	$11, %ecx
	movzwl	%si, %edx
	imull	%edx, %ecx
	cmpl	%ecx, %edi
	jae	L32
	movl	%ecx, -68(%ebp)
	movl	$2048, %eax
	subl	%edx, %eax
	movzbl	-36(%ebp), %ecx
	sarl	$5, %eax
	movl	$1, -80(%ebp)
	movl	-72(%ebp), %edx
	addl	%esi, %eax
	movl	-16(%ebp), %esi
	movw	%ax, (%edx)
	movl	-20(%ebp), %eax
	andl	-32(%ebp), %eax
	movzbl	-21(%ebp), %edx
	sall	%cl, %eax
	movl	$8, %ecx
	subl	-36(%ebp), %ecx
	sarl	%cl, %edx
	addl	%edx, %eax
	imull	$1536, %eax, %eax
	cmpl	$6, -40(%ebp)
	leal	3692(%esi,%eax), %eax
	movl	%eax, -72(%ebp)
	jle	L49
	movl	-20(%ebp), %eax
	movl	24(%ebp), %edx
	subl	-44(%ebp), %eax
	movzbl	(%edx,%eax), %eax
	movl	%eax, -84(%ebp)
L34:
	sall	-84(%ebp)
	movl	-72(%ebp), %esi
	movl	-80(%ebp), %edx
	movl	-84(%ebp), %ecx
	addl	%edx, %edx
	andl	$256, %ecx
	movl	%ecx, -88(%ebp)
	leal	(%esi,%ecx,2), %eax
	addl	%edx, %eax
	cmpl	$16777215, -68(%ebp)
	movl	%edx, -92(%ebp)
	movl	%eax, -96(%ebp)
	ja	L37
	cmpl	-64(%ebp), %ebx
	je	L155
	sall	$8, -68(%ebp)
	sall	$8, %edi
	movzbl	(%ebx), %eax
	incl	%ebx
	orl	%eax, %edi
L37:
	movl	-96(%ebp), %eax
	movl	-68(%ebp), %ecx
	movzwl	512(%eax), %esi
	shrl	$11, %ecx
	movzwl	%si, %edx
	imull	%edx, %ecx
	cmpl	%ecx, %edi
	jae	L39
	movl	%ecx, -68(%ebp)
	movl	$2048, %eax
	subl	%edx, %eax
	sarl	$5, %eax
	movl	-96(%ebp), %edx
	addl	%esi, %eax
	cmpl	$0, -88(%ebp)
	movl	-92(%ebp), %ecx
	movw	%ax, 512(%edx)
	movl	%ecx, -80(%ebp)
	je	L36
	jmp	L33
L39:
	subl	%ecx, -68(%ebp)
	movl	%esi, %eax
	movl	-96(%ebp), %esi
	shrl	$5, %edx
	subl	%ecx, %edi
	subl	%edx, %eax
	movw	%ax, 512(%esi)
	movl	-92(%ebp), %eax
	incl	%eax
	cmpl	$0, -88(%ebp)
	movl	%eax, -80(%ebp)
	je	L33
L36:
	cmpl	$255, -80(%ebp)
	jle	L34
	jmp	L137
L33:
	cmpl	$255, -80(%ebp)
	jg	L137
L49:
	movl	-80(%ebp), %edx
	movl	-72(%ebp), %ecx
	addl	%edx, %edx
	movl	%edx, -104(%ebp)
	addl	%edx, %ecx
	cmpl	$16777215, -68(%ebp)
	movl	%ecx, -100(%ebp)
	ja	L45
	cmpl	-64(%ebp), %ebx
	je	L155
	sall	$8, -68(%ebp)
	sall	$8, %edi
	movzbl	(%ebx), %eax
	incl	%ebx
	orl	%eax, %edi
L45:
	movl	-100(%ebp), %eax
	movl	-68(%ebp), %ecx
	movzwl	(%eax), %esi
	shrl	$11, %ecx
	movzwl	%si, %edx
	imull	%edx, %ecx
	cmpl	%ecx, %edi
	jae	L47
	movl	%ecx, -68(%ebp)
	movl	$2048, %eax
	subl	%edx, %eax
	movl	-104(%ebp), %ecx
	sarl	$5, %eax
	movl	-100(%ebp), %edx
	addl	%esi, %eax
	movl	%ecx, -80(%ebp)
	movw	%ax, (%edx)
	jmp	L33
L47:
	subl	%ecx, -68(%ebp)
	movl	%esi, %eax
	movl	-100(%ebp), %esi
	shrl	$5, %edx
	subl	%ecx, %edi
	subl	%edx, %eax
	movw	%ax, (%esi)
	movl	-104(%ebp), %eax
	incl	%eax
	movl	%eax, -80(%ebp)
	jmp	L33
L137:
	movzbl	-80(%ebp), %edx
	movl	-20(%ebp), %esi
	movl	24(%ebp), %eax
	movb	%dl, -21(%ebp)
	movb	%dl, (%esi,%eax)
	incl	%esi
	cmpl	$3, -40(%ebp)
	movl	%esi, -20(%ebp)
	jg	L50
	movl	$0, -40(%ebp)
	jmp	L28
L50:
	cmpl	$9, -40(%ebp)
	jg	L52
	subl	$3, -40(%ebp)
	jmp	L28
L52:
	subl	$6, -40(%ebp)
	jmp	L28
L32:
	subl	%ecx, -68(%ebp)
	shrl	$5, %edx
	movl	%esi, %eax
	subl	%edx, %eax
	subl	%ecx, %edi
	movl	-16(%ebp), %esi
	cmpl	$16777215, -68(%ebp)
	movl	-40(%ebp), %ecx
	movl	-72(%ebp), %edx
	leal	(%esi,%ecx,2), %ecx
	movw	%ax, (%edx)
	movl	%ecx, -108(%ebp)
	ja	L55
	cmpl	-64(%ebp), %ebx
	je	L155
	sall	$8, -68(%ebp)
	sall	$8, %edi
	movzbl	(%ebx), %eax
	incl	%ebx
	orl	%eax, %edi
L55:
	movl	-108(%ebp), %eax
	movl	-68(%ebp), %ecx
	movzwl	384(%eax), %esi
	shrl	$11, %ecx
	movzwl	%si, %edx
	imull	%edx, %ecx
	cmpl	%ecx, %edi
	jae	L57
	movl	%ecx, -68(%ebp)
	movl	$2048, %eax
	subl	%edx, %eax
	movl	-108(%ebp), %edx
	sarl	$5, %eax
	addl	%esi, %eax
	movl	-48(%ebp), %esi
	movl	-52(%ebp), %ecx
	movw	%ax, 384(%edx)
	movl	-44(%ebp), %eax
	movl	%esi, -52(%ebp)
	movl	-16(%ebp), %edx
	movl	%ecx, -56(%ebp)
	movl	%eax, -48(%ebp)
	xorl	%eax, %eax
	cmpl	$6, -40(%ebp)
	setg	%al
	leal	(%eax,%eax,2), %eax
	movl	%eax, -40(%ebp)
	addl	$1636, %edx
	movl	%edx, -72(%ebp)
	jmp	L60
L57:
	subl	%ecx, -68(%ebp)
	shrl	$5, %edx
	movl	%esi, %eax
	subl	%ecx, %edi
	subl	%edx, %eax
	movl	-108(%ebp), %ecx
	cmpl	$16777215, -68(%ebp)
	movw	%ax, 384(%ecx)
	ja	L61
	cmpl	-64(%ebp), %ebx
	je	L155
	sall	$8, -68(%ebp)
	sall	$8, %edi
	movzbl	(%ebx), %eax
	incl	%ebx
	orl	%eax, %edi
L61:
	movl	-108(%ebp), %eax
	movl	-68(%ebp), %ecx
	movzwl	408(%eax), %esi
	shrl	$11, %ecx
	movzwl	%si, %eax
	imull	%eax, %ecx
	cmpl	%ecx, %edi
	jae	L63
	movl	%ecx, -68(%ebp)
	movl	$2048, %edx
	subl	%eax, %edx
	movl	$2048, -112(%ebp)
	movl	%edx, %eax
	movl	-108(%ebp), %ecx
	sarl	$5, %eax
	movl	-76(%ebp), %edx
	addl	%esi, %eax
	movw	%ax, 408(%ecx)
	movl	-40(%ebp), %eax
	sall	$5, %eax
	addl	-16(%ebp), %eax
	cmpl	$16777215, -68(%ebp)
	leal	(%eax,%edx,2), %esi
	ja	L64
	cmpl	-64(%ebp), %ebx
	je	L155
	sall	$8, -68(%ebp)
	sall	$8, %edi
	movzbl	(%ebx), %eax
	incl	%ebx
	orl	%eax, %edi
L64:
	movzwl	480(%esi), %edx
	movl	-68(%ebp), %ecx
	movzwl	%dx, %eax
	shrl	$11, %ecx
	imull	%eax, %ecx
	cmpl	%ecx, %edi
	jae	L66
	subl	%eax, -112(%ebp)
	movl	%ecx, -68(%ebp)
	sarl	$5, -112(%ebp)
	movl	-112(%ebp), %eax
	addl	%edx, %eax
	cmpl	$0, -20(%ebp)
	movw	%ax, 480(%esi)
	je	L155
	xorl	%eax, %eax
	cmpl	$6, -40(%ebp)
	movl	24(%ebp), %ecx
	movl	-20(%ebp), %esi
	setg	%al
	leal	9(%eax,%eax), %eax
	movl	%eax, -40(%ebp)
	movl	-20(%ebp), %eax
	subl	-44(%ebp), %eax
	movzbl	(%ecx,%eax), %eax
	movb	%al, -21(%ebp)
	movb	%al, (%esi,%ecx)
	incl	%esi
	movl	%esi, -20(%ebp)
	jmp	L28
L66:
	subl	%ecx, -68(%ebp)
	subl	%ecx, %edi
	shrl	$5, %eax
	movl	%edx, %ecx
	subl	%eax, %ecx
	movw	%cx, 480(%esi)
	jmp	L71
L63:
	subl	%ecx, -68(%ebp)
	shrl	$5, %eax
	movl	%esi, %edx
	subl	%ecx, %edi
	subl	%eax, %edx
	movl	-108(%ebp), %ecx
	cmpl	$16777215, -68(%ebp)
	movw	%dx, 408(%ecx)
	ja	L72
	cmpl	-64(%ebp), %ebx
	je	L155
	sall	$8, -68(%ebp)
	sall	$8, %edi
	movzbl	(%ebx), %eax
	incl	%ebx
	orl	%eax, %edi
L72:
	movl	-108(%ebp), %eax
	movl	-68(%ebp), %ecx
	movzwl	432(%eax), %esi
	shrl	$11, %ecx
	movzwl	%si, %edx
	imull	%edx, %ecx
	cmpl	%ecx, %edi
	jae	L74
	movl	%ecx, -68(%ebp)
	movl	$2048, %eax
	subl	%edx, %eax
	movl	-108(%ebp), %edx
	sarl	$5, %eax
	addl	%esi, %eax
	movw	%ax, 432(%edx)
	movl	-48(%ebp), %eax
	jmp	L75
L74:
	subl	%ecx, -68(%ebp)
	shrl	$5, %edx
	movl	%esi, %eax
	subl	%ecx, %edi
	subl	%edx, %eax
	movl	-108(%ebp), %ecx
	cmpl	$16777215, -68(%ebp)
	movw	%ax, 432(%ecx)
	ja	L76
	cmpl	-64(%ebp), %ebx
	je	L155
	sall	$8, -68(%ebp)
	sall	$8, %edi
	movzbl	(%ebx), %eax
	incl	%ebx
	orl	%eax, %edi
L76:
	movl	-108(%ebp), %eax
	movl	-68(%ebp), %ecx
	movzwl	456(%eax), %esi
	shrl	$11, %ecx
	movzwl	%si, %edx
	imull	%edx, %ecx
	cmpl	%ecx, %edi
	jae	L78
	movl	%ecx, -68(%ebp)
	movl	$2048, %eax
	subl	%edx, %eax
	movl	-108(%ebp), %edx
	sarl	$5, %eax
	addl	%esi, %eax
	movw	%ax, 456(%edx)
	movl	-52(%ebp), %eax
	jmp	L79
L78:
	subl	%ecx, -68(%ebp)
	movl	%esi, %eax
	subl	%ecx, %edi
	movl	-52(%ebp), %esi
	shrl	$5, %edx
	movl	-108(%ebp), %ecx
	subl	%edx, %eax
	movw	%ax, 456(%ecx)
	movl	-56(%ebp), %eax
	movl	%esi, -56(%ebp)
L79:
	movl	-48(%ebp), %edx
	movl	%edx, -52(%ebp)
L75:
	movl	-44(%ebp), %ecx
	movl	%eax, -44(%ebp)
	movl	%ecx, -48(%ebp)
L71:
	xorl	%eax, %eax
	cmpl	$6, -40(%ebp)
	movl	-16(%ebp), %esi
	setg	%al
	leal	8(%eax,%eax,2), %eax
	addl	$2664, %esi
	movl	%eax, -40(%ebp)
	movl	%esi, -72(%ebp)
L60:
	cmpl	$16777215, -68(%ebp)
	ja	L82
	cmpl	-64(%ebp), %ebx
	je	L155
	sall	$8, -68(%ebp)
	sall	$8, %edi
	movzbl	(%ebx), %eax
	incl	%ebx
	orl	%eax, %edi
L82:
	movl	-72(%ebp), %eax
	movl	-68(%ebp), %ecx
	movzwl	(%eax), %esi
	shrl	$11, %ecx
	movzwl	%si, %edx
	imull	%edx, %ecx
	cmpl	%ecx, %edi
	jae	L84
	sall	$4, -76(%ebp)
	movl	$2048, %eax
	subl	%edx, %eax
	movl	%ecx, -68(%ebp)
	movl	-72(%ebp), %edx
	sarl	$5, %eax
	movl	$0, -120(%ebp)
	movl	-76(%ebp), %ecx
	addl	%esi, %eax
	movw	%ax, (%edx)
	leal	4(%edx,%ecx), %ecx
	movl	%ecx, -124(%ebp)
	jmp	L159
L84:
	subl	%ecx, -68(%ebp)
	shrl	$5, %edx
	movl	%esi, %eax
	subl	%edx, %eax
	subl	%ecx, %edi
	movl	-72(%ebp), %esi
	cmpl	$16777215, -68(%ebp)
	movw	%ax, (%esi)
	ja	L86
	cmpl	-64(%ebp), %ebx
	je	L155
	sall	$8, -68(%ebp)
	sall	$8, %edi
	movzbl	(%ebx), %eax
	incl	%ebx
	orl	%eax, %edi
L86:
	movl	-72(%ebp), %eax
	movl	-68(%ebp), %ecx
	movzwl	2(%eax), %esi
	shrl	$11, %ecx
	movzwl	%si, %edx
	imull	%edx, %ecx
	cmpl	%ecx, %edi
	jae	L88
	sall	$4, -76(%ebp)
	movl	$2048, %eax
	subl	%edx, %eax
	movl	%ecx, -68(%ebp)
	movl	-72(%ebp), %edx
	sarl	$5, %eax
	movl	$8, -120(%ebp)
	movl	-76(%ebp), %ecx
	addl	%esi, %eax
	movw	%ax, 2(%edx)
	leal	260(%edx,%ecx), %ecx
	movl	%ecx, -124(%ebp)
L159:
	movl	$3, -116(%ebp)
	jmp	L85
L88:
	subl	%ecx, -68(%ebp)
	movl	%esi, %eax
	movl	-72(%ebp), %esi
	movl	$16, -120(%ebp)
	shrl	$5, %edx
	subl	%ecx, %edi
	movl	$8, -116(%ebp)
	subl	%edx, %eax
	movw	%ax, 2(%esi)
	addl	$516, %esi
	movl	%esi, -124(%ebp)
L85:
	movl	$1, -60(%ebp)
	movl	-116(%ebp), %eax
	movl	%eax, -128(%ebp)
L90:
	movl	-60(%ebp), %edx
	movl	-124(%ebp), %ecx
	addl	%edx, %edx
	movl	%edx, -136(%ebp)
	addl	%edx, %ecx
	cmpl	$16777215, -68(%ebp)
	movl	%ecx, -132(%ebp)
	ja	L93
	cmpl	-64(%ebp), %ebx
	je	L155
	sall	$8, -68(%ebp)
	sall	$8, %edi
	movzbl	(%ebx), %eax
	incl	%ebx
	orl	%eax, %edi
L93:
	movl	-132(%ebp), %eax
	movl	-68(%ebp), %ecx
	movzwl	(%eax), %esi
	shrl	$11, %ecx
	movzwl	%si, %edx
	imull	%edx, %ecx
	cmpl	%ecx, %edi
	jae	L95
	movl	%ecx, -68(%ebp)
	movl	$2048, %eax
	subl	%edx, %eax
	movl	-136(%ebp), %ecx
	sarl	$5, %eax
	movl	-132(%ebp), %edx
	addl	%esi, %eax
	movl	%ecx, -60(%ebp)
	movw	%ax, (%edx)
	jmp	L92
L95:
	subl	%ecx, -68(%ebp)
	movl	%esi, %eax
	movl	-132(%ebp), %esi
	shrl	$5, %edx
	subl	%ecx, %edi
	subl	%edx, %eax
	movw	%ax, (%esi)
	movl	-136(%ebp), %eax
	incl	%eax
	movl	%eax, -60(%ebp)
L92:
	decl	-128(%ebp)
	jne	L90
	movzbl	-116(%ebp), %ecx
	movl	$1, %eax
	movl	-120(%ebp), %esi
	sall	%cl, %eax
	subl	%eax, -60(%ebp)
	addl	%esi, -60(%ebp)
	cmpl	$3, -40(%ebp)
	jg	L97
	addl	$7, -40(%ebp)
	movl	-60(%ebp), %eax
	cmpl	$3, %eax
	jle	L98
	movl	$3, %eax
L98:
	movl	$6, -140(%ebp)
	movl	-16(%ebp), %edx
	sall	$7, %eax
	leal	864(%edx,%eax), %eax
	movl	$1, %edx
	movl	%eax, -72(%ebp)
L99:
	movl	-72(%ebp), %ecx
	addl	%edx, %edx
	movl	%edx, -148(%ebp)
	addl	%edx, %ecx
	cmpl	$16777215, -68(%ebp)
	movl	%ecx, -144(%ebp)
	ja	L102
	cmpl	-64(%ebp), %ebx
	je	L155
	sall	$8, -68(%ebp)
	sall	$8, %edi
	movzbl	(%ebx), %eax
	incl	%ebx
	orl	%eax, %edi
L102:
	movl	-144(%ebp), %eax
	movl	-68(%ebp), %ecx
	movzwl	(%eax), %esi
	shrl	$11, %ecx
	movzwl	%si, %edx
	imull	%edx, %ecx
	cmpl	%ecx, %edi
	jae	L104
	movl	%ecx, -68(%ebp)
	movl	$2048, %eax
	subl	%edx, %eax
	movl	-144(%ebp), %edx
	sarl	$5, %eax
	addl	%esi, %eax
	movw	%ax, (%edx)
	movl	-148(%ebp), %edx
	jmp	L101
L104:
	subl	%ecx, -68(%ebp)
	shrl	$5, %edx
	movl	%esi, %eax
	subl	%edx, %eax
	subl	%ecx, %edi
	movl	-148(%ebp), %edx
	movl	-144(%ebp), %ecx
	incl	%edx
	movw	%ax, (%ecx)
L101:
	decl	-140(%ebp)
	jne	L99
	subl	$64, %edx
	cmpl	$3, %edx
	movl	%edx, -44(%ebp)
	jle	L122
	movl	%edx, %eax
	movl	%edx, %ecx
	sarl	%eax
	andl	$1, %ecx
	leal	-1(%eax), %esi
	orl	$2, %ecx
	movl	%esi, -152(%ebp)
	cmpl	$13, %edx
	movl	%ecx, -44(%ebp)
	jg	L107
	movzbl	-152(%ebp), %ecx
	addl	%edx, %edx
	sall	%cl, -44(%ebp)
	movl	-16(%ebp), %ecx
	movl	-44(%ebp), %esi
	leal	(%ecx,%esi,2), %eax
	subl	%edx, %eax
	addl	$1374, %eax
	movl	%eax, -72(%ebp)
	jmp	L108
L107:
	subl	$5, %eax
	movl	%eax, -152(%ebp)
L109:
	cmpl	$16777215, -68(%ebp)
	ja	L112
	cmpl	-64(%ebp), %ebx
	je	L155
	sall	$8, -68(%ebp)
	sall	$8, %edi
	movzbl	(%ebx), %eax
	incl	%ebx
	orl	%eax, %edi
L112:
	shrl	-68(%ebp)
	sall	-44(%ebp)
	cmpl	-68(%ebp), %edi
	jb	L111
	subl	-68(%ebp), %edi
	orl	$1, -44(%ebp)
L111:
	decl	-152(%ebp)
	jne	L109
	sall	$4, -44(%ebp)
	movl	-16(%ebp), %esi
	movl	$4, -152(%ebp)
	addl	$1604, %esi
	movl	%esi, -72(%ebp)
L108:
	movl	$1, -156(%ebp)
	movl	$1, %eax
L115:
	movl	-72(%ebp), %edx
	addl	%eax, %eax
	movl	%eax, -164(%ebp)
	addl	%eax, %edx
	cmpl	$16777215, -68(%ebp)
	movl	%edx, -160(%ebp)
	ja	L118
	cmpl	-64(%ebp), %ebx
	je	L155
	sall	$8, -68(%ebp)
	sall	$8, %edi
	movzbl	(%ebx), %eax
	incl	%ebx
	orl	%eax, %edi
L118:
	movl	-160(%ebp), %eax
	movl	-68(%ebp), %ecx
	movzwl	(%eax), %esi
	shrl	$11, %ecx
	movzwl	%si, %edx
	imull	%edx, %ecx
	cmpl	%ecx, %edi
	jae	L120
	movl	%ecx, -68(%ebp)
	movl	$2048, %eax
	subl	%edx, %eax
	movl	-160(%ebp), %edx
	sarl	$5, %eax
	addl	%esi, %eax
	movw	%ax, (%edx)
	movl	-164(%ebp), %eax
	jmp	L121
L120:
	subl	%ecx, -68(%ebp)
	subl	%ecx, %edi
	movl	-160(%ebp), %ecx
	movl	%esi, %eax
	shrl	$5, %edx
	subl	%edx, %eax
	movw	%ax, (%ecx)
	movl	-156(%ebp), %esi
	movl	-164(%ebp), %eax
	orl	%esi, -44(%ebp)
	incl	%eax
L121:
	sall	-156(%ebp)
	decl	-152(%ebp)
	jne	L115
L122:
	incl	-44(%ebp)
	je	L29
L97:
	addl	$2, -60(%ebp)
	movl	-20(%ebp), %eax
	cmpl	%eax, -44(%ebp)
	ja	L155
	movl	24(%ebp), %eax
	movl	-20(%ebp), %ecx
	subl	-44(%ebp), %eax
	addl	%eax, %ecx
L125:
	movzbl	(%ecx), %edx
	incl	%ecx
	movl	-20(%ebp), %esi
	movl	24(%ebp), %eax
	movb	%dl, -21(%ebp)
	movb	%dl, (%esi,%eax)
	incl	%esi
	decl	-60(%ebp)
	movl	28(%ebp), %edx
	movl	%esi, -20(%ebp)
	setne	%al
	cmpl	%edx, %esi
	setb	%dl
	movzbl	%dl, %edx
	testl	%eax, %edx
	jne	L125
L28:
	movl	28(%ebp), %ecx
	cmpl	%ecx, -20(%ebp)
	jb	L128
L29:
	cmpl	$16777215, -68(%ebp)
	ja	L129
	cmpl	-64(%ebp), %ebx
	movl	$1, %eax
	je	L18
	jmp	L130
L155:
	movl	$1, %eax
	jmp	L18
L130:
	incl	%ebx
L129:
	subl	12(%ebp), %ebx
	movl	-20(%ebp), %eax
	movl	20(%ebp), %esi
	movl	32(%ebp), %edx
	movl	%ebx, (%esi)
	movl	%eax, (%edx)
	xorl	%eax, %eax
L18:
	addl	$152, %esp
	popl	%ebx
	popl	%esi
	popl	%edi
	popl	%ebp
	ret
