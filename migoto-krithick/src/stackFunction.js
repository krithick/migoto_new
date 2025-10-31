export const pushToStack = (item) => {
    
    let stack = JSON.parse(localStorage.getItem('pathLocation')) || [];

    if (!stack.includes(item)) {
        stack.push(item);
        localStorage.setItem('pathLocation', JSON.stringify(stack));
    }

    return stack;
};

export const peekOfStack = () => {
    
    let stack = JSON.parse(localStorage.getItem('pathLocation')) || [];

    return  stack.at(-1);

};

export const popFromStack = () => {
    let stack = JSON.parse(localStorage.getItem('pathLocation')) || [];

    stack.pop();

    localStorage.setItem('pathLocation', JSON.stringify(stack));

    return stack;
};

export const RemoveFromStack = (data) => {
    let stack = JSON.parse(localStorage.getItem('pathLocation')) || [];

    while (stack.length > 0) {
        if (stack[stack.length - 1] === data) {
          break;
        }
        stack.pop();
    }
    
    localStorage.setItem('pathLocation', JSON.stringify(stack));

    return stack;
};
